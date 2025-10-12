export const name = "quillmodules";

import 'quill-mention/autoregister';
import 'quill-mention';
import Quill from 'quill';
import QuillImageDropAndPaste from 'quill-image-drop-and-paste';
import BlotFormatter from '@enzedonline/quill-blot-formatter2';
import htmlEditButton from "quill-html-edit-button";
import QuillBetterTable from "quill-better-table";
import React from 'react';
import { RegisterImportPool } from "./Base";

import "@enzedonline/quill-blot-formatter2/dist/css/quill-blot-formatter2.css"; // align styles

// import { EmbedBlot } from "parchment";
// const BreakBlot = Quill.import("blots/break");

Quill.register('modules/imageDropAndPaste', QuillImageDropAndPaste);
Quill.register('modules/blotFormatter2', BlotFormatter);
Quill.register('modules/htmlEditButton', htmlEditButton);
Quill.register('modules/better-table', QuillBetterTable);
// Quill.register(BreakBlot);

const QuillImageData = QuillImageDropAndPaste.ImageData;

let ex; const exModulePromises = ex = {
    queryString:  import(/* webpackChunkName: "queryString_quillmodules" */"query-string"),
};RegisterImportPool(ex);


export const quillLoad = (elem, quill) => {}


export const onTextChange = (elem, e) => {
    // console.log("onTextChange", e);
    // cleans up the trailing new line (\n)
    const plainValue = e.textValue.slice(0, -1);
    let value = (elem.state.plain ? plainValue : e.htmlValue ) || "";

    // When an image is seleted and on CTRL+S, before deselecting
    // the image blotFormatter2 resets the --resize-width property;
    // some transitional state. Clean it out.
    // value = value.replace(/--resize-width:\s*0px;?/g, "");
    // better yet instead of cleaning it out, replace the value with img.width
    // if (!elem.state.plain && e.source !== "user") {
    //     const el = document.createElement("div");
    //     el.innerHTML = value;
    //     el.querySelectorAll("img[width]").forEach(img => {
    //         const widthAttr = img.getAttribute("width").split("px")[0];
    //         if (!widthAttr) return;
    //
    //         const parent = img.closest("[style]");
    //         if (parent) {
    //             const cssWidth = parent.style.getPropertyValue("--resize-width");
    //             if (cssWidth === "0px" || cssWidth === "") {
    //                 parent.style.setProperty("--resize-width", widthAttr + "px");
    //             }
    //         }
    //     })
    //     value = el.innerHTML;
    // }
    //
    // console.log(e.source, value);
    // if (!elem.state.plain) {
    //     const el = document.createElement("div");
    //     el.innerHTML = value;
    //     el.querySelectorAll("img").forEach(img => {
    //       // Prefer style.width, fallback to attribute
    //       let w = img.style.width || img.getAttribute("width");
    //       if (w) {
    //         w = w.replace("px", "");
    //         img.setAttribute("width", w);
    //         img.style.width = w + "px"; // keep inline for display
    //       }
    //     });
    //     value = el.innerHTML;
    // }

    // if (e.source === "user") elem.update({[elem.dataKey]: value});
    elem.update({[elem.dataKey]: value});
    // elem.setState({})
    // elem.setState({});
    // elem.updateValue(value);
}


export const getQuillModules = (
    APP, silentFetch, signal, mentionValues, i18n, elem, hasToolbar = true
) => {
    const modules = {
        mention: quillMention({
            silentFetch: silentFetch,
            signal: signal,
            mentionValues: mentionValues,
        }),
        blotFormatter2: {
            debug: true,
            resize: {
                useRelativeSize: true,
            },
        },
        table: false,
        "better-table": {
            operationMenu: {
                // items: {
                //     mergeCells: {
                //         text: i18n.t("Merge cells"),
                //     }
                // },
            }
        }
    }
    if (hasToolbar) {
        modules.htmlEditButton = {
            msg: i18n.t('Edit HTML here, when you click "OK" the quill editor\'s contents will be replaced'),
            prependSelector: "div#raw-editor-container",
            okText: i18n.t("Ok"),
            cancelText: i18n.t("Cancel"),
            buttonTitle: i18n.t("Show HTML source"),
        }
    }
    if (APP.state.site_data.installed_plugins.includes('uploads'))
        modules.imageDropAndPaste = {handler: imageHandler(elem)};
    modules.keyboard = {
        bindings: {
            ...QuillBetterTable.keyboardBindings,
            tab: {
                key: 9,
                handler: (range, context) => {
                    return true;
                },
            },
            home: {
                key: "Home",
                handler: (range, context) => {
                    const { quill } = ex;
                    let [line, offset] = quill.getLine(range.index);
                    if (line && line.domNode.tagName === "LI") {
                      // Move to the start of text inside the list item
                      quill.setSelection(line.offset(quill.scroll), 0, "user");
                      return false; // stop default browser behavior
                    }
                    return true;
                },
            }
        }
    }
    return modules;
}


export const overrideImageButtonHandler = (quill) => {
    quill.getModule('toolbar').addHandler('image', (clicked) => {
        if (clicked) {
            let fileInput;
            // fileInput = quill.container.querySelector('input.ql-image[type=file]');
            // if (fileInput == null) {
                fileInput = document.createElement('input');
                fileInput.setAttribute('type', 'file');
                fileInput.setAttribute('accept', 'image/png, image/gif, image/jpeg, image/bmp, image/x-icon');
                fileInput.classList.add('ql-image');
                fileInput.addEventListener('change', (e) => {
                    const files = e.target.files;
                    let file;
                    if (files.length > 0) {
                        file = files[0];
                        const type = file.type;
                        const reader = new FileReader();
                        reader.onload = (e) => {
                            const dataURL = e.target.result;
                            imageHandler({quill})(
                                dataURL,
                                type,
                                new QuillImageData(dataURL, type, file.name)
                            );
                            fileInput.value = '';
                        }
                        reader.readAsDataURL(file);
                    }
                })
            // }
            fileInput.click();
        }
    })
}

export const imageHandler = (elem) => {
    return (imageDataURL, type, imageData) => {
        const quill = elem.quill;
        let index = (quill.getSelection() || {}).index;
        if (index === undefined || index < 0) index = quill.getLength();
        quill.insertEmbed(index, 'image', imageDataURL);
    }

    // const imageEl = quill.root.querySelector(`img[src="${imageDataURL}"]`);
    // Set default height
    // imageEl.setAttribute("height", window.App.URLContext.root.chInPx.offsetHeight * 20);
}

export const quillMention = ({silentFetch, signal, mentionValues}) => {
    function mentionSource(searchTerm, renderList, mentionChar) {
        if (searchTerm.length === 0) {
            let values = mentionValues[mentionChar];
            renderList(values, searchTerm);
        } else {
            ex.resolve(['queryString']).then(({queryString}) => {
                silentFetch({path: `suggestions?${queryString.default.stringify({
                    query: searchTerm, trigger: mentionChar})}`, signal: signal})
                .then(data => renderList(data.suggestions, searchTerm));
            });
        }
    }

    return {
        allowedChars: /^[A-Za-z0-9\s]*$/,
        mentionDenotationChars: window.App.state.site_data.suggestors,
        source: mentionSource,
        listItemClass: "ql-mention-list-item",
        mentionContainerClass: "ql-mention-list-container",
        mentionListClass: "ql-mention-list",
        dataAttributes: ["value", "link", "title", "denotationChar"],
    }
}

const quillToolbarHeaderTemplate = <React.Fragment>
    <span className="ql-formats">
        <select className='ql-header' defaultValue='0'>
            <option value='1'>Heading</option>
            <option value='2'>Subheading</option>
            <option value='0'>Normal</option>
        </select>
        <select className='ql-font'>
            <option defaultValue={true}></option>
            <option value='serif'></option>
            <option value='monospace'></option>
        </select>
    </span>
    <span className="ql-formats">
        <select className="ql-size">
            <option value="small"></option>
            <option defaultValue={true}></option>
            <option value="large"></option>
            <option value="huge"></option>
        </select>
    </span>
    <span className="ql-formats">
        <button className="ql-script" value="sub"></button>
        <button className="ql-script" value="super"></button>
    </span>
    <span className="ql-formats">
        <button type='button' className='ql-bold' aria-label='Bold'></button>
        <button type='button' className='ql-italic' aria-label='Italic'></button>
        <button type='button' className='ql-underline' aria-label='Underline'></button>
    </span>
    <span className="ql-formats">
        <select className='ql-color'></select>
        <select className='ql-background'></select>
    </span>
    <span className="ql-formats">
        <button type='button' className='ql-list' value='ordered' aria-label='Ordered List'></button>
        <button type='button' className='ql-list' value='bullet' aria-label='Unordered List'></button>
        <select className='ql-align'>
            <option defaultValue={true}></option>
            <option value='center'></option>
            <option value='right'></option>
            <option value='justify'></option>
        </select>
    </span>
    <span className="ql-formats">
        <button type='button' className='ql-link' aria-label='Insert Link'></button>
        <button type='button' className='ql-image' aria-label='Insert Image'></button>
        <button type='button' className='ql-code-block' aria-label='Insert Code Block'></button>
    </span>
    <span className="ql-formats">
        <button type='button' className='ql-clean' aria-label='Remove Styles'></button>
    </span>
</React.Fragment>

export const invokeRefInsert = (elem) => {
    const { APP } = elem.props.urlParams.controller;
    const { URLContext } = APP;
    let index = (elem.quill.getSelection() || {}).index;
    if (index === undefined || index < 0)
        index = elem.quill.getLength();
    URLContext.actionHandler.runAction({
        action_full_name: URLContext.actionHandler.findUniqueAction("insert_reference").full_name,
        actorId: "about.About",
        response_callback: (data) => {
            if (data.success)
                elem.quill.insertText(index, data.message);
        }
    });
}

export const refInsert = (elem) => {
    if (!elem.c.APP.state.site_data.installed_plugins.includes('memo'))
        return null;
    return <span className="ql-formats">
        <button type='button'
            onClick={(e) => invokeRefInsert(elem)}
            aria-label='Open link dialog'>
            <i className="pi pi-link"></i></button>
    </span>
}

const commonHeader = (elem) => {
    return <>
        {quillToolbarHeaderTemplate}
        {refInsert(elem)}
        <span className="ql-formats">
            <button type="button"
                onClick={e => {
                    const bt = elem.quill.getModule("better-table");
                    bt.insertTable(3, 3);
                }}>
                <i className="pi pi-table"></i></button>
        </span>
    </>
}

export const quillToolbar = {
    header: quillToolbarHeaderTemplate,
    commonHeader: commonHeader,
}

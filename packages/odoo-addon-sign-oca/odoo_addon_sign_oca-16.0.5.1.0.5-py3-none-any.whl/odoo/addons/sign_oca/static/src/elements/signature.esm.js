/** @odoo-module **/

import {SignatureDialog} from "@web/core/signature/signature_dialog";
import core from "web.core";
import {registry} from "@web/core/registry";

const signatureSignOca = {
    uploadSignature: function (parent, item, signatureItem, data) {
        item.value = data.signatureImage[1];
        parent.postIframeField(item);
        parent.checkFilledAll();
        var next_items = _.filter(
            parent.info.items,
            (i) => i.tabindex > item.tabindex
        ).sort((a, b) => a.tabindex - b.tabindex);
        if (next_items.length > 0) {
            const nextItem = next_items[0];
            if (nextItem && parent.items && parent.items[nextItem.id]) {
                parent.items[nextItem.id].dispatchEvent(new Event("focus_signature"));
            }
        }
    },
    generate: function (parent, item, signatureItem) {
        var input = $(
            core.qweb.render("sign_oca.sign_iframe_field_signature", {item: item})
        )[0];
        if (item.role_id === parent.info.role_id) {
            const requestOpenDialog = () => {
                if (!item.dialogOpened) {
                    item.dialogOpened = true;
                    var signatureOptions = {
                        fontColor: "DarkBlue",
                        defaultName: parent.info.partner.name,
                    };
                    parent.env.services.dialog.add(
                        SignatureDialog,
                        {
                            ...signatureOptions,
                            uploadSignature: (data) =>
                                this.uploadSignature(parent, item, signatureItem, data),
                        },
                        {
                            onClose: () => {
                                item.dialogOpened = false;
                            },
                        }
                    );
                }
            };

            signatureItem[0].addEventListener("focus_signature", () => {
                requestOpenDialog();
            });
            input.addEventListener("click", (ev) => {
                ev.preventDefault();
                ev.stopPropagation();
                requestOpenDialog();
            });
            input.addEventListener("keydown", (ev) => {
                if ((ev.keyCode || ev.which) !== 9) {
                    return true;
                }
                ev.preventDefault();
                var next_items = _.filter(
                    parent.info.items,
                    (i) =>
                        i.tabindex > item.tabindex && i.role_id === parent.info.role_id
                );
                if (next_items.length > 0) {
                    ev.currentTarget.blur();
                    const nextItem = next_items[0];
                    if (nextItem && parent.items && parent.items[nextItem.id]) {
                        parent.items[nextItem.id].dispatchEvent(
                            new Event("focus_signature")
                        );
                    }
                }
            });
        }
        return input;
    },
    check: function (item) {
        return Boolean(item.value);
    },
};
registry.category("sign_oca").add("signature", signatureSignOca);

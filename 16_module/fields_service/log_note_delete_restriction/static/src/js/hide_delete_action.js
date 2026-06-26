/** @odoo-module **/

import { messageActionsRegistry } from "@mail/core/common/message_actions";
import { Composer } from "@mail/core/common/composer";
import { patch } from "@web/core/utils/patch";

const deleteAction = messageActionsRegistry.get("delete");

/** Check whether the current user is an administrator. **/
function isAdmin(store) {
    return Boolean(store?.self?.main_user_id?.is_admin);
}

/** Fetch the delete reason wizard action from the backend. **/
async function getDeleteWizardAction(env, messageId) {
    const action = await env.services.orm.call(
        "mail.message",
        "action_open_delete_reason_wizard",
        [[messageId]]
    );

    if (!action || action.type !== "ir.actions.act_window") {
        return null;
    }

    return {
        ...action,
        views: action.views || [[action.view_id || false, "form"]],
    };
}

/** Open delete reason wizard.**/
async function openDeleteWizard(env, message, onClose = () => {}) {
    const action = await getDeleteWizardAction(env, message.id);

    if (!action) {
        return;
    }
    env.services.action.doAction(action, { onClose });
}

/** Override delete action visibility and behavior. **/
messageActionsRegistry.add(
    "delete",
    {
        ...deleteAction,

        condition: ({ message, store }) => {
            return isAdmin(store) && message.editable;
        },

        onSelected: async ({ message, owner, thread }) => {
            await openDeleteWizard(
                owner.env,
                message,
                () => thread?.fetchNewMessages?.()
            );
        },
    },
    { force: true }
);

/** Replace delete confirmation popup with delete reason wizard. **/
patch(Composer.prototype, {
    async editMessage() {
        if (!this.askDeleteFromEdit) {
            return super.editMessage();
        }

        const message = this.props.composer?.message;

        if (!message) {
            return super.editMessage();
        }

        const store = message.store;

        if (!isAdmin(store)) {
            return super.editMessage();
        }

        const thread = message.thread;

        await openDeleteWizard(
            this.env,
            message,
            () => {
                message.exitEditMode?.(thread);
                thread?.fetchNewMessages?.();
            }
        );
    },
});

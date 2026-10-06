"""JSON-Schema der Entscheidungen des Modells."""



# ============================================================
# JSON-SCHEMA
# ============================================================

COMMAND_SCHEMA = {
    "oneOf": [

        # ----------------------------------------------------
        # VIEW
        # ----------------------------------------------------

        {
            "type": "object",
            "properties": {
                "operation": {
                    "const": "view"
                },
                "path": {
                    "type": "string",
                    "minLength": 1
                },
                "reason": {
                    "type": "string"
                }
            },
            "required": [
                "operation",
                "path",
                "reason"
            ],
            "additionalProperties": False
        },

        # ----------------------------------------------------
        # CREATE FILE
        # ----------------------------------------------------

        {
            "type": "object",
            "properties": {
                "operation": {
                    "const": "create"
                },
                "path": {
                    "type": "string",
                    "minLength": 1
                },
                "kind": {
                    "const": "file"
                },
                "content": {
                    "type": "string"
                },
                "reason": {
                    "type": "string"
                }
            },
            "required": [
                "operation",
                "path",
                "kind",
                "content",
                "reason"
            ],
            "additionalProperties": False
        },

        # ----------------------------------------------------
        # CREATE DIRECTORY
        # ----------------------------------------------------

        {
            "type": "object",
            "properties": {
                "operation": {
                    "const": "create"
                },
                "path": {
                    "type": "string",
                    "minLength": 1
                },
                "kind": {
                    "const": "directory"
                },
                "reason": {
                    "type": "string"
                }
            },
            "required": [
                "operation",
                "path",
                "kind",
                "reason"
            ],
            "additionalProperties": False
        },

        # ----------------------------------------------------
        # EDIT
        # ----------------------------------------------------

        {
            "type": "object",
            "properties": {
                "operation": {
                    "const": "edit"
                },
                "path": {
                    "type": "string",
                    "minLength": 1
                },
                "content": {
                    "type": "string"
                },
                "reason": {
                    "type": "string"
                }
            },
            "required": [
                "operation",
                "path",
                "content",
                "reason"
            ],
            "additionalProperties": False
        },

        # ----------------------------------------------------
        # DELETE
        # ----------------------------------------------------

        {
            "type": "object",
            "properties": {
                "operation": {
                    "const": "delete"
                },
                "path": {
                    "type": "string",
                    "minLength": 1
                },
                "reason": {
                    "type": "string"
                }
            },
            "required": [
                "operation",
                "path",
                "reason"
            ],
            "additionalProperties": False
        },

        # ----------------------------------------------------
        # EXECUTE
        # ----------------------------------------------------

        {
            "type": "object",
            "properties": {
                "operation": {
                    "const": "execute"
                },
                "path": {
                    "type": "string",
                    "minLength": 1
                },
                "reason": {
                    "type": "string"
                }
            },
            "required": [
                "operation",
                "path",
                "reason"
            ],
            "additionalProperties": False
        },

        # ----------------------------------------------------
        # NONE
        # ----------------------------------------------------

        {
            "type": "object",
            "properties": {
                "operation": {
                    "const": "none"
                },
                "reason": {
                    "type": "string"
                }
            },
            "required": [
                "operation",
                "reason"
            ],
            "additionalProperties": False
        }
    ]
}


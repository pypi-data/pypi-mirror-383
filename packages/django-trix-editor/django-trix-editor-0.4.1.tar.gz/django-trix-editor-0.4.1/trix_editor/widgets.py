from django import forms
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe

TRIX_VERSION = getattr(settings, 'TRIX_VERSION', '2.1.15')


class JSPath:
    def __html__(self):
        return (
            f'<script type="text/javascript" src="//unpkg.com/trix@{TRIX_VERSION}/dist/trix.umd.min.js"></script>'
        )


class JSCode:
    def __html__(self):
        return (
            """
            <script type="text/javascript">
                function getCookie(name) {
                    let cookieValue = null;
                    if (document.cookie && document.cookie !== '') {
                        const cookies = document.cookie.split(';');
                        for (let i = 0; i < cookies.length; i++) {
                            let cookie = cookies[i].trim();
                            // Does this cookie string begin with the name we want?
                            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                break;
                            }
                        }
                    }
                    return cookieValue;
                }

                addEventListener("trix-attachment-add", function (event) {
                    if (event.attachment.file) {
                        handleUpload(event.attachment)
                    }
                })

                function handleUpload(attachment) {
                    uploadFile(attachment.file, setProgress, setAttributes)
                
                    function setProgress(progress) {
                        attachment.setUploadProgress(progress)
                    }
                
                    function setAttributes(attributes) {
                        attachment.setAttributes(attributes)
                    }
                }

                function uploadFile(file, progressCallback, successCallback) {
                    var formData = new FormData()
                    var xhr = new XMLHttpRequest()
                    formData.append("Content-Type", file.type)
                    formData.append("file", file)
                    xhr.open("POST", \"""" + reverse('trix_editor_upload') + """", true)
                    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"))
                    xhr.upload.addEventListener("progress", function (event) {
                        progressCallback(event.loaded / event.total * 100)
                    })
                    xhr.addEventListener("load", function (event) {
                        if (xhr.status === 200) {
                            let attributes = {
                                url: JSON.parse(xhr.responseText).attachment_url
                            }
                            successCallback(attributes)
                        }
                    })
                    xhr.send(formData)
                }
            </script>
            """
        )


class CSSPath:
    def __html__(self):
        return (
            f'<link rel="stylesheet" href="https://unpkg.com/trix@{TRIX_VERSION}/dist/trix.css">'
        )


class CSSAdminCode:
    def __html__(self):
        return (
            """
            <style>                 
                trix-editor, 
                trix-toolbar .trix-button-group,
                trix-toolbar .trix-button {
                    border-color: var(--border-color) !important;
                }

                /* Url dialog */
                trix-toolbar .trix-dialog,
                trix-toolbar .trix-input--dialog {
                    background: var(--body-bg) !important;
                }
                trix-toolbar .trix-input--dialog:focus {
                    border-color: var(--body-quiet-color);
                }

                html[data-theme="dark"] {
                    trix-toolbar .trix-button:before {
                        filter: invert();
                    }
                    trix-editor {
                        color: white;
                    }
                    trix-toolbar .trix-button:before:disabled {
                        filter: invert() grayscale(1) brightness(2);
                    }
                    trix-toolbar .trix-button--icon::before {
                        opacity: 1;
                    }
                    trix-toolbar .trix-button--icon:disabled::before {
                        opacity: 0.5;
                    }
                    trix-toolbar .trix-button.trix-active {
                        background: var(--button-bg) !important;
                    }

                    /* Url dialog */
                    trix-toolbar .trix-input--dialog {
                        color: white;
                    }
                    trix-toolbar .trix-button--dialog {
                        color: white;
                    }
                }
            </style>
            """
        )


class TrixEditorWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs['hidden'] = True
        html = super().render(name, value, attrs=attrs, renderer=renderer)
        return mark_safe(f'{html}<div><trix-editor input="{attrs["id"]}"></trix-editor></div>')

    class Media:
        js = [
            JSCode(),
            JSPath(),
        ]
        css = {
            'all': [
                CSSAdminCode(),
                CSSPath(),
            ],
        }

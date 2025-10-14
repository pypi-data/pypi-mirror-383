# V1

## Devices

Types:

```python
from gbox_sdk.types.v1 import DeviceInfo, GetDeviceListResponse, DeviceToBoxResponse
```

Methods:

- <code title="get /devices">client.v1.devices.<a href="./src/gbox_sdk/resources/v1/devices.py">list</a>(\*\*<a href="src/gbox_sdk/types/v1/device_list_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/get_device_list_response.py">GetDeviceListResponse</a></code>
- <code title="get /devices/{deviceId}">client.v1.devices.<a href="./src/gbox_sdk/resources/v1/devices.py">get</a>(device_id) -> <a href="./src/gbox_sdk/types/v1/device_info.py">DeviceInfo</a></code>
- <code title="post /devices/{deviceId}/box">client.v1.devices.<a href="./src/gbox_sdk/resources/v1/devices.py">to_box</a>(device_id, \*\*<a href="src/gbox_sdk/types/v1/device_to_box_params.py">params</a>) -> str</code>

## Boxes

Types:

```python
from gbox_sdk.types.v1 import (
    AndroidBox,
    CreateAndroidBox,
    CreateLinuxBox,
    LinuxBox,
    BoxRetrieveResponse,
    BoxListResponse,
    BoxDisplayResponse,
    BoxExecuteCommandsResponse,
    BoxLiveViewURLResponse,
    BoxResolutionSetResponse,
    BoxRunCodeResponse,
    BoxStartResponse,
    BoxStopResponse,
    BoxWebTerminalURLResponse,
    BoxWebsocketURLResponse,
)
```

Methods:

- <code title="get /boxes/{boxId}">client.v1.boxes.<a href="./src/gbox_sdk/resources/v1/boxes/boxes.py">retrieve</a>(box_id) -> <a href="./src/gbox_sdk/types/v1/box_retrieve_response.py">BoxRetrieveResponse</a></code>
- <code title="get /boxes">client.v1.boxes.<a href="./src/gbox_sdk/resources/v1/boxes/boxes.py">list</a>(\*\*<a href="src/gbox_sdk/types/v1/box_list_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/box_list_response.py">BoxListResponse</a></code>
- <code title="post /boxes/android">client.v1.boxes.<a href="./src/gbox_sdk/resources/v1/boxes/boxes.py">create_android</a>(\*\*<a href="src/gbox_sdk/types/v1/box_create_android_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/android_box.py">AndroidBox</a></code>
- <code title="post /boxes/linux">client.v1.boxes.<a href="./src/gbox_sdk/resources/v1/boxes/boxes.py">create_linux</a>(\*\*<a href="src/gbox_sdk/types/v1/box_create_linux_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/linux_box.py">LinuxBox</a></code>
- <code title="get /boxes/{boxId}/display">client.v1.boxes.<a href="./src/gbox_sdk/resources/v1/boxes/boxes.py">display</a>(box_id) -> <a href="./src/gbox_sdk/types/v1/box_display_response.py">BoxDisplayResponse</a></code>
- <code title="post /boxes/{boxId}/commands">client.v1.boxes.<a href="./src/gbox_sdk/resources/v1/boxes/boxes.py">execute_commands</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/box_execute_commands_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/box_execute_commands_response.py">BoxExecuteCommandsResponse</a></code>
- <code title="post /boxes/{boxId}/live-view-url">client.v1.boxes.<a href="./src/gbox_sdk/resources/v1/boxes/boxes.py">live_view_url</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/box_live_view_url_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/box_live_view_url_response.py">BoxLiveViewURLResponse</a></code>
- <code title="post /boxes/{boxId}/resolution">client.v1.boxes.<a href="./src/gbox_sdk/resources/v1/boxes/boxes.py">resolution_set</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/box_resolution_set_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/box_resolution_set_response.py">BoxResolutionSetResponse</a></code>
- <code title="post /boxes/{boxId}/run-code">client.v1.boxes.<a href="./src/gbox_sdk/resources/v1/boxes/boxes.py">run_code</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/box_run_code_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/box_run_code_response.py">BoxRunCodeResponse</a></code>
- <code title="post /boxes/{boxId}/start">client.v1.boxes.<a href="./src/gbox_sdk/resources/v1/boxes/boxes.py">start</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/box_start_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/box_start_response.py">BoxStartResponse</a></code>
- <code title="post /boxes/{boxId}/stop">client.v1.boxes.<a href="./src/gbox_sdk/resources/v1/boxes/boxes.py">stop</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/box_stop_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/box_stop_response.py">BoxStopResponse</a></code>
- <code title="post /boxes/{boxId}/terminate">client.v1.boxes.<a href="./src/gbox_sdk/resources/v1/boxes/boxes.py">terminate</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/box_terminate_params.py">params</a>) -> None</code>
- <code title="post /boxes/{boxId}/web-terminal-url">client.v1.boxes.<a href="./src/gbox_sdk/resources/v1/boxes/boxes.py">web_terminal_url</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/box_web_terminal_url_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/box_web_terminal_url_response.py">BoxWebTerminalURLResponse</a></code>
- <code title="get /boxes/{boxId}/websocket-url">client.v1.boxes.<a href="./src/gbox_sdk/resources/v1/boxes/boxes.py">websocket_url</a>(box_id) -> <a href="./src/gbox_sdk/types/v1/box_websocket_url_response.py">BoxWebsocketURLResponse</a></code>

### Storage

Types:

```python
from gbox_sdk.types.v1.boxes import StoragePresignedURLResponse
```

Methods:

- <code title="post /boxes/{boxId}/storage/presigned-url">client.v1.boxes.storage.<a href="./src/gbox_sdk/resources/v1/boxes/storage.py">presigned_url</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/storage_presigned_url_params.py">params</a>) -> str</code>

### Actions

Types:

```python
from gbox_sdk.types.v1.boxes import (
    ActionCommonOptions,
    ActionResult,
    ActionScreenshotOptions,
    DetectedElement,
    ActionClipboardGetResponse,
    ActionElementsDetectResponse,
    ActionExtractResponse,
    ActionRecordingStopResponse,
    ActionRewindExtractResponse,
    ActionScreenLayoutResponse,
    ActionScreenshotResponse,
    ActionSettingsResponse,
    ActionSettingsResetResponse,
    ActionSettingsUpdateResponse,
)
```

Methods:

- <code title="post /boxes/{boxId}/actions/click">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">click</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_click_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/action_result.py">ActionResult</a></code>
- <code title="get /boxes/{boxId}/actions/clipboard">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">clipboard_get</a>(box_id) -> str</code>
- <code title="post /boxes/{boxId}/actions/clipboard">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">clipboard_set</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_clipboard_set_params.py">params</a>) -> None</code>
- <code title="post /boxes/{boxId}/actions/drag">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">drag</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_drag_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/action_result.py">ActionResult</a></code>
- <code title="post /boxes/{boxId}/actions/elements/detect">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">elements_detect</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_elements_detect_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/action_elements_detect_response.py">ActionElementsDetectResponse</a></code>
- <code title="post /boxes/{boxId}/actions/extract">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">extract</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_extract_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/action_extract_response.py">ActionExtractResponse</a></code>
- <code title="post /boxes/{boxId}/actions/long-press">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">long_press</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_long_press_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/action_result.py">ActionResult</a></code>
- <code title="post /boxes/{boxId}/actions/move">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">move</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_move_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/action_result.py">ActionResult</a></code>
- <code title="post /boxes/{boxId}/actions/press-button">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">press_button</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_press_button_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/action_result.py">ActionResult</a></code>
- <code title="post /boxes/{boxId}/actions/press-key">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">press_key</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_press_key_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/action_result.py">ActionResult</a></code>
- <code title="post /boxes/{boxId}/actions/recording/start">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">recording_start</a>(box_id) -> None</code>
- <code title="post /boxes/{boxId}/actions/recording/stop">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">recording_stop</a>(box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/action_recording_stop_response.py">ActionRecordingStopResponse</a></code>
- <code title="delete /boxes/{boxId}/actions/recording/rewind">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">rewind_disable</a>(box_id) -> None</code>
- <code title="post /boxes/{boxId}/actions/recording/rewind">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">rewind_enable</a>(box_id) -> None</code>
- <code title="post /boxes/{boxId}/actions/recording/rewind/extract">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">rewind_extract</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_rewind_extract_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/action_rewind_extract_response.py">ActionRewindExtractResponse</a></code>
- <code title="get /boxes/{boxId}/actions/screen-layout">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">screen_layout</a>(box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/action_screen_layout_response.py">ActionScreenLayoutResponse</a></code>
- <code title="post /boxes/{boxId}/actions/screen-rotation">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">screen_rotation</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_screen_rotation_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/action_result.py">ActionResult</a></code>
- <code title="post /boxes/{boxId}/actions/screenshot">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">screenshot</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_screenshot_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/action_screenshot_response.py">ActionScreenshotResponse</a></code>
- <code title="post /boxes/{boxId}/actions/scroll">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">scroll</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_scroll_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/action_result.py">ActionResult</a></code>
- <code title="get /boxes/{boxId}/actions/settings">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">settings</a>(box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/action_settings_response.py">ActionSettingsResponse</a></code>
- <code title="delete /boxes/{boxId}/actions/settings">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">settings_reset</a>(box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/action_settings_reset_response.py">ActionSettingsResetResponse</a></code>
- <code title="put /boxes/{boxId}/actions/settings">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">settings_update</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_settings_update_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/action_settings_update_response.py">ActionSettingsUpdateResponse</a></code>
- <code title="post /boxes/{boxId}/actions/swipe">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">swipe</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_swipe_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/action_result.py">ActionResult</a></code>
- <code title="post /boxes/{boxId}/actions/tap">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">tap</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_tap_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/action_result.py">ActionResult</a></code>
- <code title="post /boxes/{boxId}/actions/touch">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">touch</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_touch_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/action_result.py">ActionResult</a></code>
- <code title="post /boxes/{boxId}/actions/type">client.v1.boxes.actions.<a href="./src/gbox_sdk/resources/v1/boxes/actions.py">type</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/action_type_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/action_result.py">ActionResult</a></code>

### Proxy

Types:

```python
from gbox_sdk.types.v1.boxes import ProxyGetResponse, ProxySetResponse
```

Methods:

- <code title="delete /boxes/{boxId}/proxy">client.v1.boxes.proxy.<a href="./src/gbox_sdk/resources/v1/boxes/proxy.py">clear</a>(box_id) -> None</code>
- <code title="get /boxes/{boxId}/proxy">client.v1.boxes.proxy.<a href="./src/gbox_sdk/resources/v1/boxes/proxy.py">get</a>(box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/proxy_get_response.py">ProxyGetResponse</a></code>
- <code title="post /boxes/{boxId}/proxy">client.v1.boxes.proxy.<a href="./src/gbox_sdk/resources/v1/boxes/proxy.py">set</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/proxy_set_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/proxy_set_response.py">ProxySetResponse</a></code>

### Media

Types:

```python
from gbox_sdk.types.v1.boxes import (
    MediaAlbum,
    MediaPhoto,
    MediaVideo,
    MediaGetMediaResponse,
    MediaGetMediaSupportResponse,
    MediaListAlbumsResponse,
    MediaListMediaResponse,
)
```

Methods:

- <code title="post /boxes/{boxId}/media/albums">client.v1.boxes.media.<a href="./src/gbox_sdk/resources/v1/boxes/media.py">create_album</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/media_create_album_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/media_album.py">MediaAlbum</a></code>
- <code title="delete /boxes/{boxId}/media/albums/{albumName}">client.v1.boxes.media.<a href="./src/gbox_sdk/resources/v1/boxes/media.py">delete_album</a>(album_name, \*, box_id) -> None</code>
- <code title="delete /boxes/{boxId}/media/albums/{albumName}/media/{mediaName}">client.v1.boxes.media.<a href="./src/gbox_sdk/resources/v1/boxes/media.py">delete_media</a>(media_name, \*, box_id, album_name) -> None</code>
- <code title="get /boxes/{boxId}/media/albums/{albumName}/media/{mediaName}/download">client.v1.boxes.media.<a href="./src/gbox_sdk/resources/v1/boxes/media.py">download_media</a>(media_name, \*, box_id, album_name) -> BinaryAPIResponse</code>
- <code title="get /boxes/{boxId}/media/albums/{albumName}">client.v1.boxes.media.<a href="./src/gbox_sdk/resources/v1/boxes/media.py">get_album_detail</a>(album_name, \*, box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/media_album.py">MediaAlbum</a></code>
- <code title="get /boxes/{boxId}/media/albums/{albumName}/media/{mediaName}">client.v1.boxes.media.<a href="./src/gbox_sdk/resources/v1/boxes/media.py">get_media</a>(media_name, \*, box_id, album_name) -> <a href="./src/gbox_sdk/types/v1/boxes/media_get_media_response.py">MediaGetMediaResponse</a></code>
- <code title="get /boxes/{boxId}/media/support">client.v1.boxes.media.<a href="./src/gbox_sdk/resources/v1/boxes/media.py">get_media_support</a>(box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/media_get_media_support_response.py">MediaGetMediaSupportResponse</a></code>
- <code title="get /boxes/{boxId}/media/albums">client.v1.boxes.media.<a href="./src/gbox_sdk/resources/v1/boxes/media.py">list_albums</a>(box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/media_list_albums_response.py">MediaListAlbumsResponse</a></code>
- <code title="get /boxes/{boxId}/media/albums/{albumName}/media">client.v1.boxes.media.<a href="./src/gbox_sdk/resources/v1/boxes/media.py">list_media</a>(album_name, \*, box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/media_list_media_response.py">MediaListMediaResponse</a></code>
- <code title="patch /boxes/{boxId}/media/albums/{albumName}">client.v1.boxes.media.<a href="./src/gbox_sdk/resources/v1/boxes/media.py">update_album</a>(album_name, \*, box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/media_update_album_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/media_album.py">MediaAlbum</a></code>

### Fs

Types:

```python
from gbox_sdk.types.v1.boxes import (
    Dir,
    File,
    FListResponse,
    FExistsResponse,
    FInfoResponse,
    FReadResponse,
    FRemoveResponse,
    FRenameResponse,
)
```

Methods:

- <code title="get /boxes/{boxId}/fs/list">client.v1.boxes.fs.<a href="./src/gbox_sdk/resources/v1/boxes/fs.py">list</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/f_list_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/f_list_response.py">FListResponse</a></code>
- <code title="post /boxes/{boxId}/fs/exists">client.v1.boxes.fs.<a href="./src/gbox_sdk/resources/v1/boxes/fs.py">exists</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/f_exists_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/f_exists_response.py">FExistsResponse</a></code>
- <code title="get /boxes/{boxId}/fs/info">client.v1.boxes.fs.<a href="./src/gbox_sdk/resources/v1/boxes/fs.py">info</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/f_info_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/f_info_response.py">FInfoResponse</a></code>
- <code title="get /boxes/{boxId}/fs/read">client.v1.boxes.fs.<a href="./src/gbox_sdk/resources/v1/boxes/fs.py">read</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/f_read_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/f_read_response.py">FReadResponse</a></code>
- <code title="delete /boxes/{boxId}/fs">client.v1.boxes.fs.<a href="./src/gbox_sdk/resources/v1/boxes/fs.py">remove</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/f_remove_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/f_remove_response.py">FRemoveResponse</a></code>
- <code title="post /boxes/{boxId}/fs/rename">client.v1.boxes.fs.<a href="./src/gbox_sdk/resources/v1/boxes/fs.py">rename</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/f_rename_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/f_rename_response.py">FRenameResponse</a></code>
- <code title="post /boxes/{boxId}/fs/write">client.v1.boxes.fs.<a href="./src/gbox_sdk/resources/v1/boxes/fs.py">write</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/f_write_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/file.py">File</a></code>

### Browser

Types:

```python
from gbox_sdk.types.v1.boxes import (
    BrowserCdpURLResponse,
    BrowserCloseTabResponse,
    BrowserGetProxyResponse,
    BrowserGetTabsResponse,
    BrowserOpenResponse,
    BrowserOpenTabResponse,
    BrowserSwitchTabResponse,
    BrowserUpdateTabResponse,
)
```

Methods:

- <code title="post /boxes/{boxId}/browser/connect-url/cdp">client.v1.boxes.browser.<a href="./src/gbox_sdk/resources/v1/boxes/browser.py">cdp_url</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/browser_cdp_url_params.py">params</a>) -> str</code>
- <code title="delete /boxes/{boxId}/browser/proxy">client.v1.boxes.browser.<a href="./src/gbox_sdk/resources/v1/boxes/browser.py">clear_proxy</a>(box_id) -> None</code>
- <code title="delete /boxes/{boxId}/browser/close">client.v1.boxes.browser.<a href="./src/gbox_sdk/resources/v1/boxes/browser.py">close</a>(box_id) -> None</code>
- <code title="delete /boxes/{boxId}/browser/tabs/{tabId}">client.v1.boxes.browser.<a href="./src/gbox_sdk/resources/v1/boxes/browser.py">close_tab</a>(tab_id, \*, box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/browser_close_tab_response.py">BrowserCloseTabResponse</a></code>
- <code title="get /boxes/{boxId}/browser/proxy">client.v1.boxes.browser.<a href="./src/gbox_sdk/resources/v1/boxes/browser.py">get_proxy</a>(box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/browser_get_proxy_response.py">BrowserGetProxyResponse</a></code>
- <code title="get /boxes/{boxId}/browser/tabs">client.v1.boxes.browser.<a href="./src/gbox_sdk/resources/v1/boxes/browser.py">get_tabs</a>(box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/browser_get_tabs_response.py">BrowserGetTabsResponse</a></code>
- <code title="post /boxes/{boxId}/browser/open">client.v1.boxes.browser.<a href="./src/gbox_sdk/resources/v1/boxes/browser.py">open</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/browser_open_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/browser_open_response.py">BrowserOpenResponse</a></code>
- <code title="post /boxes/{boxId}/browser/tabs">client.v1.boxes.browser.<a href="./src/gbox_sdk/resources/v1/boxes/browser.py">open_tab</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/browser_open_tab_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/browser_open_tab_response.py">BrowserOpenTabResponse</a></code>
- <code title="post /boxes/{boxId}/browser/proxy">client.v1.boxes.browser.<a href="./src/gbox_sdk/resources/v1/boxes/browser.py">set_proxy</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/browser_set_proxy_params.py">params</a>) -> None</code>
- <code title="post /boxes/{boxId}/browser/tabs/{tabId}/switch">client.v1.boxes.browser.<a href="./src/gbox_sdk/resources/v1/boxes/browser.py">switch_tab</a>(tab_id, \*, box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/browser_switch_tab_response.py">BrowserSwitchTabResponse</a></code>
- <code title="put /boxes/{boxId}/browser/tabs/{tabId}">client.v1.boxes.browser.<a href="./src/gbox_sdk/resources/v1/boxes/browser.py">update_tab</a>(tab_id, \*, box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/browser_update_tab_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/browser_update_tab_response.py">BrowserUpdateTabResponse</a></code>

### Android

Types:

```python
from gbox_sdk.types.v1.boxes import (
    AndroidApp,
    AndroidPkg,
    AndroidGetConnectAddressResponse,
    AndroidInstallResponse,
    AndroidListActivitiesResponse,
    AndroidListAppResponse,
    AndroidListPkgResponse,
    AndroidListPkgSimpleResponse,
)
```

Methods:

- <code title="post /boxes/{boxId}/android/packages/{packageName}/backup">client.v1.boxes.android.<a href="./src/gbox_sdk/resources/v1/boxes/android.py">backup</a>(package_name, \*, box_id) -> BinaryAPIResponse</code>
- <code title="post /boxes/{boxId}/android/packages/backup-all">client.v1.boxes.android.<a href="./src/gbox_sdk/resources/v1/boxes/android.py">backup_all</a>(box_id) -> BinaryAPIResponse</code>
- <code title="post /boxes/{boxId}/android/packages/{packageName}/close">client.v1.boxes.android.<a href="./src/gbox_sdk/resources/v1/boxes/android.py">close</a>(package_name, \*, box_id) -> None</code>
- <code title="post /boxes/{boxId}/android/packages/close-all">client.v1.boxes.android.<a href="./src/gbox_sdk/resources/v1/boxes/android.py">close_all</a>(box_id) -> None</code>
- <code title="get /boxes/{boxId}/android/packages/{packageName}">client.v1.boxes.android.<a href="./src/gbox_sdk/resources/v1/boxes/android.py">get</a>(package_name, \*, box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/android_pkg.py">AndroidPkg</a></code>
- <code title="get /boxes/{boxId}/android/apps/{packageName}">client.v1.boxes.android.<a href="./src/gbox_sdk/resources/v1/boxes/android.py">get_app</a>(package_name, \*, box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/android_app.py">AndroidApp</a></code>
- <code title="get /boxes/{boxId}/android/connect-address">client.v1.boxes.android.<a href="./src/gbox_sdk/resources/v1/boxes/android.py">get_connect_address</a>(box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/android_get_connect_address_response.py">AndroidGetConnectAddressResponse</a></code>
- <code title="post /boxes/{boxId}/android/packages">client.v1.boxes.android.<a href="./src/gbox_sdk/resources/v1/boxes/android.py">install</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/android_install_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/android_install_response.py">AndroidInstallResponse</a></code>
- <code title="get /boxes/{boxId}/android/packages/{packageName}/activities">client.v1.boxes.android.<a href="./src/gbox_sdk/resources/v1/boxes/android.py">list_activities</a>(package_name, \*, box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/android_list_activities_response.py">AndroidListActivitiesResponse</a></code>
- <code title="get /boxes/{boxId}/android/apps">client.v1.boxes.android.<a href="./src/gbox_sdk/resources/v1/boxes/android.py">list_app</a>(box_id) -> <a href="./src/gbox_sdk/types/v1/boxes/android_list_app_response.py">AndroidListAppResponse</a></code>
- <code title="get /boxes/{boxId}/android/packages">client.v1.boxes.android.<a href="./src/gbox_sdk/resources/v1/boxes/android.py">list_pkg</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/android_list_pkg_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/android_list_pkg_response.py">AndroidListPkgResponse</a></code>
- <code title="get /boxes/{boxId}/android/packages/simple">client.v1.boxes.android.<a href="./src/gbox_sdk/resources/v1/boxes/android.py">list_pkg_simple</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/android_list_pkg_simple_params.py">params</a>) -> <a href="./src/gbox_sdk/types/v1/boxes/android_list_pkg_simple_response.py">AndroidListPkgSimpleResponse</a></code>
- <code title="post /boxes/{boxId}/android/packages/{packageName}/open">client.v1.boxes.android.<a href="./src/gbox_sdk/resources/v1/boxes/android.py">open</a>(package_name, \*, box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/android_open_params.py">params</a>) -> None</code>
- <code title="post /boxes/{boxId}/android/packages/{packageName}/restart">client.v1.boxes.android.<a href="./src/gbox_sdk/resources/v1/boxes/android.py">restart</a>(package_name, \*, box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/android_restart_params.py">params</a>) -> None</code>
- <code title="post /boxes/{boxId}/android/packages/restore">client.v1.boxes.android.<a href="./src/gbox_sdk/resources/v1/boxes/android.py">restore</a>(box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/android_restore_params.py">params</a>) -> None</code>
- <code title="delete /boxes/{boxId}/android/packages/{packageName}">client.v1.boxes.android.<a href="./src/gbox_sdk/resources/v1/boxes/android.py">uninstall</a>(package_name, \*, box_id, \*\*<a href="src/gbox_sdk/types/v1/boxes/android_uninstall_params.py">params</a>) -> None</code>

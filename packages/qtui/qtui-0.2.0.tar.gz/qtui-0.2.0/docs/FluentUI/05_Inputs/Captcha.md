# Fluent UI 캡차 (FluCaptcha)

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluCaptcha` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 사용자 입력이 사람에 의한 것인지, 아니면 자동화된 봇에 의한 것인지 구별하기 위한 간단한 이미지 기반 CAPTCHA(캡차)를 생성하고 표시하는 기능을 제공합니다.

내부적으로는 Python으로 구현된 `QQuickPaintedItem`이며, 무작위 문자와 노이즈(점, 선)를 포함하는 이미지를 동적으로 생성합니다.

## 공통 임포트 방법

`FluCaptcha` 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluCaptcha

`FluCaptcha`는 4자리의 무작위 문자(숫자, 영문 대문자, 영문 소문자)를 생성하고, 이를 왜곡 및 노이즈가 포함된 이미지 형태로 렌더링합니다. 사용자는 이 이미지에 표시된 문자를 식별하여 입력해야 하며, 애플리케이션은 `verify()` 메소드를 통해 입력된 코드의 정확성을 검증할 수 있습니다. 이는 회원가입, 로그인, 게시글 작성 등에서 자동화된 스팸 및 어뷰징을 방지하는 기본적인 수단으로 사용될 수 있습니다.

### 기반 클래스

Python `QQuickPaintedItem` (QML에서는 `Item`과 유사하게 사용 가능)

### 주요 프로퍼티

| 이름         | 타입   | 기본값                      | 설명                                                                                                  |
| :----------- | :----- | :-------------------------- | :---------------------------------------------------------------------------------------------------- |
| `font`       | `QFont`| (PixelSize=28, Bold=True) | 캡차 이미지 내의 문자를 렌더링하는 데 사용될 폰트 객체입니다.                                                             |
| `ignoreCase` | `bool` | `true`                      | `verify()` 메소드 호출 시, 입력된 코드와 실제 코드 간의 대소문자를 구분할지 여부입니다. `true`이면 대소문자를 무시하고 비교합니다. |

### 주요 메소드

| 이름      | 파라미터        | 반환타입 | 설명                                                                                              |
| :-------- | :-------------- | :------- | :------------------------------------------------------------------------------------------------ |
| `refresh` | -               | `void`   | 새로운 4자리 무작위 코드를 생성하고, 노이즈를 포함한 캡차 이미지를 다시 그립니다. 사용자가 새 캡차를 요청할 때 호출합니다.             |
| `verify`  | `code: string`  | `bool`   | 사용자가 입력한 `code` 문자열을 현재 캡차가 가지고 있는 실제 코드와 비교합니다. `ignoreCase` 설정에 따라 비교하며, 일치하면 `true`, 불일치하면 `false`를 반환합니다. |

### 고유 시그널

QML에서 직접 연결하여 사용할 수 있는 고유 시그널은 없습니다. (`fontChanged`, `ignoreCaseChanged`는 내부 Python 프로퍼티 시스템용입니다.)

---

## 예제

다음은 `FluCaptcha`를 표시하고, 이미지를 클릭하거나 "Refresh" 버튼을 눌러 새로고침하며, `FluTextBox`에 입력된 값으로 `verify()` 메소드를 호출하여 검증하는 예제입니다 (`T_Captcha.qml` 기반).

```qml
import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import FluentUI 1.0

FluScrollablePage {
    title: qsTr("Captcha")
    padding: 20

    ColumnLayout {
        spacing: 15

        // FluCaptcha 표시 및 클릭으로 새로고침
        FluCaptcha {
            id: captcha
            // ignoreCase 프로퍼티를 스위치와 바인딩
            ignoreCase: switchCase.checked 
            
            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    captcha.refresh() // 클릭 시 refresh() 메소드 호출
                }
            }
        }

        // 새로고침 버튼
        FluButton {
            text: qsTr("Refresh")
            onClicked: {
                captcha.refresh() // 버튼 클릭 시 refresh() 메소드 호출
            }
        }

        // 대소문자 무시 옵션 스위치
        FluToggleSwitch {
            id: switchCase
            text: qsTr("Ignore Case")
            checked: true // 기본값은 대소문자 무시
        }

        // 사용자 입력 및 검증 영역
        RowLayout {
            spacing: 10
            
            FluTextBox {
                id: textBox
                placeholderText: qsTr("Please enter a verification code")
                Layout.preferredWidth: 240
            }
            
            FluButton {
                text: qsTr("Verify")
                onClicked: {
                    // verify() 메소드 호출 및 결과 처리
                    var success = captcha.verify(textBox.text)
                    if (success) {
                        // 검증 성공 시 로직 (예: 팝업 메시지 표시)
                        showSuccess(qsTr("The verification code is correct"))
                    } else {
                        // 검증 실패 시 로직 (예: 오류 메시지 표시 및 새로고침)
                        showError(qsTr("Error validation, please re-enter"))
                        textBox.text = "" // 입력 필드 비우기
                        captcha.refresh() // 새 코드로 새로고침
                    }
                }
            }
        }
    }
}
```

---

## 참고 사항

*   **Python 구현**: `FluCaptcha`는 Python(`FluCaptcha.py`)으로 구현된 `QQuickPaintedItem`입니다. 따라서 이 컴포넌트를 사용하기 위해서는 PySide6 기반의 Python 환경이 설정되어 있어야 합니다.
*   **외부 라이브러리 불필요**: CAPTCHA 이미지 생성 및 표시에 필요한 기능(무작위 생성, 그리기)은 표준 Qt 및 Python 모듈을 사용하므로, `qrcode`나 `Chart.js`와 같은 별도의 외부 라이브러리를 설치할 필요는 없습니다.
*   **크기 및 스타일 제한**: `FluCaptcha`의 기본 크기는 180x80 픽셀로 고정되어 있으며, 내부적으로 노이즈(점, 선) 및 문자 위치를 그리는 로직이 이 크기에 맞춰 구현되어 있을 수 있습니다. QML에서 아이템의 `width`나 `height` 프로퍼티를 변경해도 캡차 내용이 올바르게 스케일링되지 않을 수 있습니다. 또한, 노이즈의 형태나 문자의 왜곡 정도 등은 현재로서는 커스터마이징할 수 없습니다.
*   **보안 강도**: 제공되는 캡차는 기본적인 수준의 봇 방지 기능을 수행합니다. 하지만 이미지 기반 캡차는 지속적으로 발전하는 OCR(광학 문자 인식) 기술 및 인공지능에 의해 우회될 가능성이 있습니다. 매우 높은 수준의 보안이 요구되는 서비스에서는 Google reCAPTCHA와 같은 더 강력한 캡차 솔루션을 도입하거나, 다중 인증 요소(MFA) 등 추가적인 보안 조치를 함께 사용하는 것을 고려해야 합니다. 
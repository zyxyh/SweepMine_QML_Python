import QtQuick 2.0
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    property int minewidth: 25
    property int sec: 0
    property int minesleft: 99
    width: frame.width + 100
    height: frame.height

    Rectangle{
        id: frame
        anchors.left: parent.left
        anchors.top: parent.top
        border.width: 2
        width: minewidth * 30
        height: minewidth * 16
        Repeater {
            id: repeater
            anchors.fill: parent
            model: minesModel
            delegate: minedelegate
        }
    }
    Rectangle{
        anchors.top: parent.top
        anchors.left: frame.right
        width: 100
        height: frame.height
        ColumnLayout {
            anchors.fill: parent
            Button {
                id: startbtn
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.leftMargin: 10
                anchors.rightMargin: 10
                anchors.topMargin: 30
                text: "Start"
                font.pixelSize: 20
                font.bold: true
                onClicked:{
                    root.sec = 0
                    minesleft = 99
                    statustext.text = ""
                    minesModel.newGame()
                }
            }
            Text{
                id: timetext
                anchors.topMargin: 30
                anchors.horizontalCenter: parent.horizontalCenter
                font.pixelSize: 30
                font.bold: true
                text: root.sec
            }
            Text{
                id: mineslefttext
                anchors.topMargin: 30
                anchors.horizontalCenter: parent.horizontalCenter
                font.pixelSize: 30
                font.bold: true
                text: root.minesleft
            }
            Text{
                id: statustext
                width: parent.width
                anchors.topMargin: 30
                font.pixelSize: 24
                font.bold: true
                color: "red"
                wrapMode: Text.WrapAnywhere
                text: ""
            }
        }
    }

    Timer {
        id: timer
        interval: 1000
        repeat: true
        triggeredOnStart: true
        onTriggered: {
            root.sec += 1
        }
    }

    function refresh(){
        switch (minesModel.getStatus())
        {
            case 1:
                minesleft = 99 - minesModel.getmarkedCount()
                statustext.text = ""
                break
            case 2:
                timer.stop()
                statustext.text = "恭喜你\n成功了"
                break
            case 3:
                timer.stop()
                statustext.text = "很不幸\n你触雷了"
                break
            default:
                break
        }
    }

    Component{
        id: minedelegate

        Rectangle{
            id: mine
            x: index % 30 * root.minewidth + 1
            y: Math.floor(index / 30) * root.minewidth + 1
            width: root.minewidth
            height: root.minewidth
            color: openedflag ? "lightgray" : "darkgray"
            border.width: 1
            border.color:"blue"

            property bool lbtnPressed: false
            property bool rbtnPressed: false

            Text{
                id: marktext
                anchors.centerIn: parent
                font.pixelSize: 24
                font.bold: true
                color: "black"
                text: openedflag ? (minesaround === 0 ? "" : minesaround) : mark
            }

            MouseArea{
                anchors.fill: parent
                acceptedButtons: Qt.LeftButton | Qt.RightButton

                onPressed: {
                    if (mouse.button === Qt.RightButton) rbtnPressed = true
                    if (mouse.button === Qt.LeftButton) lbtnPressed = true
                }
                onReleased: {

                    if(minesModel.getStatus() === 0) { timer.start() }
                    if ((minesModel.openedflag) && (lbtnPressed && rbtnPressed)) {
                            lbtnPressed = false
                            rbtnPressed = false
                            minesModel.open(index)
                    }
                    if (!minesModel.openedflag) {
                        if (mouse.button === Qt.LeftButton) {
                            lbtnPressed = false
                            minesModel.open(index)
                            //minedelegate.openSignal(index)
                        }
                        else if (mouse.button === Qt.RightButton) {
                            //minedelegate.markSignal(index)
                            minesModel.mark(index)
                            rbtnPressed = false
                        }
                    }
                    console.log(minesModel.getStatus())
                    root.refresh()
                }
            }
        }
    }
}



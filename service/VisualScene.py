import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
                             QComboBox, QListWidget, QGroupBox, QCheckBox, QScrollArea,
                             QMessageBox, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from entity.BaseModel import Conversation
from entity.Scene import Scene
from mapper.CharacterMapper import CharacterMapper
from mapper.ConversationMapper import ConversationMapper
from mapper.SceneMapper import SceneMapper


# 假设你已经导入了SceneService
# from your_module import SceneService

class SceneServiceGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scene_service = None
        self.scene = None
        self.characters = []
        self.speakers = {}
        self.chat_history = None

        self.init_ui()
        self.init_scene_service()

    def init_scene_service(self):
        """初始化场景服务"""
        try:
            # 这里需要根据你的实际情况调整导入
            from service.SceneService import SceneService  # 替换为实际的模块名

            self.scene_service = SceneService(SceneMapper(), ConversationMapper(), CharacterMapper())
            self.scene = Scene(sid="1", name="name", is_main=True, summary="", is_root=True)
            self.characters = self.scene_service.get_characters_by_scene(self.scene.sid)

            # 构建角色选择字典
            for idx, character in enumerate(self.characters):
                self.speakers[str(idx)] = character.name

            # 更新UI中的角色列表
            self.update_character_lists()

        except ImportError as e:
            QMessageBox.warning(self, "警告", f"无法导入SceneService: {e}")

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("Scene Service 可视化界面")
        self.setGeometry(100, 100, 1200, 800)

        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # 左侧控制面板
        self.create_control_panel(splitter)

        # 右侧聊天历史显示
        self.create_chat_display(splitter)

        # 设置分割器比例
        splitter.setSizes([400, 800])

    def create_control_panel(self, parent):
        """创建控制面板"""
        control_widget = QWidget()
        control_layout = QVBoxLayout()
        control_widget.setLayout(control_layout)

        # 消息输入组
        message_group = QGroupBox("消息输入")
        message_layout = QVBoxLayout()

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("输入对话(可为空)")
        self.message_input.setMaximumHeight(100)
        message_layout.addWidget(QLabel("输入对话:"))
        message_layout.addWidget(self.message_input)

        message_group.setLayout(message_layout)
        control_layout.addWidget(message_group)

        # 角色选择组
        character_group = QGroupBox("角色选择")
        character_layout = QVBoxLayout()

        # 扮演角色选择
        character_layout.addWidget(QLabel("扮演角色:"))
        self.user_character_combo = QComboBox()
        character_layout.addWidget(self.user_character_combo)

        # 消息接收者选择
        character_layout.addWidget(QLabel("消息接收者:"))
        self.recipients_list = QListWidget()
        self.recipients_list.setSelectionMode(QListWidget.MultiSelection)
        self.recipients_list.setMaximumHeight(80)
        character_layout.addWidget(self.recipients_list)

        # 回复者选择
        character_layout.addWidget(QLabel("谁需要回复:"))
        self.speakers_list = QListWidget()
        self.speakers_list.setSelectionMode(QListWidget.MultiSelection)
        self.speakers_list.setMaximumHeight(80)
        character_layout.addWidget(self.speakers_list)

        # 回复对象选择
        character_layout.addWidget(QLabel("回复给谁:"))
        self.speak_to_combo = QComboBox()
        character_layout.addWidget(self.speak_to_combo)

        # 回复可见者选择
        character_layout.addWidget(QLabel("回复谁可见:"))
        self.speaker_recipients_list = QListWidget()
        self.speaker_recipients_list.setSelectionMode(QListWidget.MultiSelection)
        self.speaker_recipients_list.setMaximumHeight(80)
        character_layout.addWidget(self.speaker_recipients_list)

        character_group.setLayout(character_layout)
        control_layout.addWidget(character_group)

        # 控制按钮
        button_layout = QHBoxLayout()

        self.start_conversation_btn = QPushButton("开始对话")
        self.start_conversation_btn.clicked.connect(self.start_conversation)
        self.start_conversation_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        self.clear_history_btn = QPushButton("清空历史")
        self.clear_history_btn.clicked.connect(self.clear_history)
        self.clear_history_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)

        button_layout.addWidget(self.start_conversation_btn)
        button_layout.addWidget(self.clear_history_btn)
        control_layout.addLayout(button_layout)

        # 添加弹性空间
        control_layout.addStretch()

        parent.addWidget(control_widget)

    def create_chat_display(self, parent):
        """创建聊天历史显示区域"""
        chat_widget = QWidget()
        chat_layout = QVBoxLayout()
        chat_widget.setLayout(chat_layout)

        chat_layout.addWidget(QLabel("聊天历史:"))

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("微软雅黑", 10))
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        chat_layout.addWidget(self.chat_display)

        parent.addWidget(chat_widget)

    def update_character_lists(self):
        """更新角色列表"""
        character_names = list(self.speakers.values())

        # 更新所有列表
        for widget in [self.recipients_list, self.speakers_list, self.speaker_recipients_list]:
            widget.clear()
            widget.addItems(character_names)

        # 更新组合框
        self.speak_to_combo.clear()
        self.speak_to_combo.addItems(character_names)

        # 更新扮演角色下拉框
        self.user_character_combo.clear()
        self.user_character_combo.addItems(character_names)

    def get_selected_items(self, list_widget):
        """获取列表中选中的项目"""
        selected_items = []
        for item in list_widget.selectedItems():
            selected_items.append(item.text())
        return selected_items

    def start_conversation(self):
        """开始对话"""
        if not self.scene_service:
            QMessageBox.warning(self, "错误", "场景服务未初始化")
            return

        try:
            # 获取用户输入
            message = self.message_input.toPlainText().strip()
            recipients = self.get_selected_items(self.recipients_list)
            speakers_names = self.get_selected_items(self.speakers_list)
            speak_to = self.speak_to_combo.currentText()
            speaker_recipients = self.get_selected_items(self.speaker_recipients_list)
            user_character = self.user_character_combo.currentText()

            # 验证必要输入
            if not user_character:
                QMessageBox.warning(self, "警告", "请选择扮演角色")
                return

            if not speakers_names:
                QMessageBox.warning(self, "警告", "请选择至少一个回复者")
                return

            if not speak_to:
                QMessageBox.warning(self, "警告", "请选择回复对象")
                return

            if not speaker_recipients:
                QMessageBox.warning(self, "警告", "请选择至少一个回复可见者")
                return

            # 创建对话对象
            conversation = Conversation(
                conversation_id=None,
                message=message,
                sid=1,
                sender_id=1,
                recipient_id=1
            )

            # 开始对话
            self.chat_history = self.scene_service.start_conversation(
                scene=self.scene,
                user_character=user_character,
                speakers=speakers_names,
                chat_history=self.chat_history,
                conversation=conversation,
                recipients=recipients,
                speak_to=speak_to,
                speaker_recipients=speaker_recipients
            )

            # 更新聊天显示
            self.update_chat_display()

            # 清空消息输入
            self.message_input.clear()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"对话过程中出现错误: {str(e)}")

    def update_chat_display(self):
        """更新聊天历史显示"""
        if not self.chat_history:
            return

        self.chat_display.clear()

        for msg in self.chat_history:
            # 格式化消息显示
            sender = msg.get("name", "Unknown")
            content = msg.get("content", "")
            recipients = msg.get("recipient", [])
            is_broadcast = msg.get("broadcast", False)

            # 移除发送者名称前缀（如果存在）
            if content.startswith(f"{sender}:"):
                content = content[len(f"{sender}:"):]

            # 构建显示文本
            display_text = f"【{sender}】"
            if is_broadcast:
                display_text += f" 广播给 {', '.join(recipients)}"
            else:
                display_text += f" 对 {', '.join(recipients)} 说"
            display_text += f": {content}\n"

            # 添加到显示区域
            self.chat_display.append(display_text)

        # 滚动到底部
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_history(self):
        """清空聊天历史"""
        self.chat_history = None
        self.chat_display.clear()
        QMessageBox.information(self, "提示", "聊天历史已清空")

    def show_current_selection_info(self, user_character, recipients, speakers, speak_to, speaker_recipients):
        """在聊天显示区域显示当前选择的信息"""
        info_text = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【本轮对话配置】
扮演角色: {user_character}
消息接收者: {', '.join(recipients) if recipients else '无'}
回复者: {', '.join(speakers)}
回复对象: {speak_to}
回复可见者: {', '.join(speaker_recipients)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        self.chat_display.append(info_text)


def main():
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyleSheet("""
        QMainWindow {
            background-color: #ffffff;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 5px;
            margin-top: 1ex;
            padding: 5px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QListWidget {
            border: 1px solid #cccccc;
            border-radius: 3px;
            background-color: #ffffff;
        }
        QComboBox {
            border: 1px solid #cccccc;
            border-radius: 3px;
            padding: 5px;
            background-color: #ffffff;
        }
        QLineEdit, QTextEdit {
            border: 1px solid #cccccc;
            border-radius: 3px;
            padding: 5px;
            background-color: #ffffff;
        }
    """)

    window = SceneServiceGUI()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

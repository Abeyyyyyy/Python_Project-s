import sys
import json
import os
from datetime import datetime
from enum import Enum
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QComboBox, QDateEdit, 
    QLabel, QMessageBox, QScrollArea, QGroupBox, QGridLayout,
    QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class Status(Enum):
    PENDING = "⏳ Pending"
    IN_PROGRESS = "🔄 In Progress"
    COMPLETED = "✅ Completed"
    CANCELLED = "❌ Cancelled"

class Task:
    def __init__(self, id, title, description="", priority=Priority.MEDIUM, 
                 due_date=None, category="General", created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = Status.PENDING
        self.due_date = due_date
        self.category = category
        self.created_at = created_at or datetime.now()
        self.completed_at = None

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority.value,
            'status': self.status.value,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'category': self.category,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    @classmethod
    def from_dict(cls, data):
        task = cls(
            data['id'],
            data['title'],
            data['description'],
            Priority(data['priority']),
            datetime.fromisoformat(data['due_date']) if data['due_date'] else None,
            data['category'],
            datetime.fromisoformat(data['created_at'])
        )
        task.status = Status(data['status'])
        task.completed_at = datetime.fromisoformat(data['completed_at']) if data['completed_at'] else None
        return task

    def is_overdue(self):
        if self.due_date and self.status != Status.COMPLETED:
            return self.due_date < datetime.now()
        return False

class TodoList:
    def __init__(self, filename="todo_data.json"):
        self.filename = filename
        self.tasks = []
        self.next_id = 1
        self.load_tasks()

    def load_tasks(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(task_data) for task_data in data['tasks']]
                    self.next_id = data['next_id']
            except Exception as e:
                print(f"Error loading tasks: {e}")
                self.tasks = []
                self.next_id = 1

    def save_tasks(self):
        try:
            data = {
                'tasks': [task.to_dict() for task in self.tasks],
                'next_id': self.next_id
            }
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving tasks: {e}")
            return False

    def add_task(self, title, description="", priority=Priority.MEDIUM, 
                 due_date=None, category="General"):
        task = Task(self.next_id, title, description, priority, due_date, category)
        self.next_id += 1
        self.tasks.append(task)
        if self.save_tasks():
            return task
        return None

    def update_task(self, task_id, **kwargs):
        task = self.get_task(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            return self.save_tasks()
        return False

    def delete_task(self, task_id):
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return self.save_tasks()
        return False

    def get_task(self, task_id):
        return next((task for task in self.tasks if task.id == task_id), None)

    def get_tasks_by_status(self, status):
        return [task for task in self.tasks if task.status == status]

    def get_tasks_by_priority(self, priority):
        return [task for task in self.tasks if task.priority == priority]

    def get_tasks_by_category(self, category):
        return [task for task in self.tasks if task.category == category]

    def get_overdue_tasks(self):
        return [task for task in self.tasks if task.is_overdue()]

    def get_statistics(self):
        total = len(self.tasks)
        completed = len(self.get_tasks_by_status(Status.COMPLETED))
        pending = len(self.get_tasks_by_status(Status.PENDING))
        in_progress = len(self.get_tasks_by_status(Status.IN_PROGRESS))
        overdue = len(self.get_overdue_tasks())
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        priority_stats = {}
        for priority in Priority:
            priority_stats[priority] = len(self.get_tasks_by_priority(priority))
            
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'overdue': overdue,
            'completion_rate': completion_rate,
            'priority_stats': priority_stats
        }

class TaskWidget(QWidget):
    taskUpdated = pyqtSignal()
    taskDeleted = pyqtSignal(int)

    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Priority indicator dengan warna
        priority_colors = {
            Priority.LOW: "#4CAF50",      # Green
            Priority.MEDIUM: "#FFC107",   # Yellow
            Priority.HIGH: "#FF9800",     # Orange
            Priority.URGENT: "#F44336"    # Red
        }
        
        priority_frame = QFrame()
        priority_frame.setFixedSize(8, 60)
        priority_frame.setStyleSheet(f"background-color: {priority_colors[self.task.priority]}; border-radius: 4px;")
        
        # Task info
        info_layout = QVBoxLayout()
        
        title_label = QLabel(self.task.title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ffffff;")
        
        desc_label = QLabel(self.task.description if self.task.description else "No description")
        desc_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        desc_label.setWordWrap(True)
        
        details_label = QLabel(f"🏷️ {self.task.category} | 📅 {self.task.due_date.strftime('%Y-%m-%d') if self.task.due_date else 'No due date'}")
        details_label.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        
        info_layout.addWidget(title_label)
        info_layout.addWidget(desc_label)
        info_layout.addWidget(details_label)
        info_layout.addStretch()
        
        # Status combo
        status_combo = QComboBox()
        status_combo.addItems([status.value for status in Status])
        status_combo.setCurrentText(self.task.status.value)
        status_combo.currentTextChanged.connect(self.update_status)
        status_combo.setFixedWidth(150)
        status_combo.setStyleSheet("""
            QComboBox {
                background-color: #404040;
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
            QComboBox QAbstractItemView {
                background-color: #404040;
                color: #ffffff;
                selection-background-color: #4CAF50;
            }
        """)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setToolTip("Delete Task")
        delete_btn.setFixedSize(40, 40)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        delete_btn.clicked.connect(self.delete_task)
        
        button_layout.addWidget(status_combo)
        button_layout.addWidget(delete_btn)
        
        # Add widgets to layout
        layout.addWidget(priority_frame)
        layout.addLayout(info_layout, 1)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setFixedHeight(80)
        self.update_style()

    def update_status(self, new_status):
        status_map = {status.value: status for status in Status}
        self.task.status = status_map[new_status]
        if self.task.status == Status.COMPLETED:
            self.task.completed_at = datetime.now()
        else:
            self.task.completed_at = None
            
        self.taskUpdated.emit()
        self.update_style()

    def update_style(self):
        if self.task.status == Status.COMPLETED:
            self.setStyleSheet("""
                QWidget {
                    background-color: #1e4620;
                    border: 2px solid #4CAF50;
                    border-radius: 10px;
                }
            """)
        elif self.task.is_overdue():
            self.setStyleSheet("""
                QWidget {
                    background-color: #5a1e1e;
                    border: 2px solid #F44336;
                    border-radius: 10px;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #363636;
                    border: 2px solid #555;
                    border-radius: 10px;
                }
            """)

    def delete_task(self):
        reply = QMessageBox.question(self, "Delete Task", 
                                   f"Are you sure you want to delete '{self.task.title}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.taskDeleted.emit(self.task.id)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.todo_list = TodoList()
        self.init_ui()
        self.load_tasks()

    def init_ui(self):
        self.setWindowTitle("🚀 Professional Todo List - Portfolio Edition")
        self.setGeometry(100, 100, 1400, 800)
        
        # Apply dark palette to the entire application
        self.set_dark_palette()
        
        # Enhanced dark theme styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #4CAF50;
            }
            QDateEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QDateEdit::drop-down {
                border: none;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #4CAF50;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton#secondary {
                background-color: #2196F3;
            }
            QPushButton#secondary:hover {
                background-color: #1976D2;
            }
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #2d2d2d;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #2d2d2d;
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
            }
            QProgressBar {
                border: 2px solid #404040;
                border-radius: 5px;
                text-align: center;
                color: white;
                font-weight: bold;
                background-color: #2d2d2d;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
            QScrollBar:vertical {
                background: #2d2d2d;
                width: 15px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #404040;
                border-radius: 7px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4a4a4a;
            }
            QMessageBox {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left sidebar
        left_sidebar = QVBoxLayout()
        left_sidebar.setSpacing(20)
        
        # Add task section
        add_task_group = QGroupBox("➕ Add New Task")
        add_task_layout = QVBoxLayout()
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter task title...")
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Enter task description...")
        self.desc_input.setMaximumHeight(100)
        
        # Form layout
        form_layout = QGridLayout()
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["🔵 Low", "🟡 Medium", "🟠 High", "🔴 Urgent"])
        
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems(["💼 Work", "🏠 Personal", "🛒 Shopping", "❤️ Health", "📚 Learning"])
        
        self.due_date = QDateEdit()
        self.due_date.setDate(QDate.currentDate().addDays(7))
        self.due_date.setCalendarPopup(True)
        
        form_layout.addWidget(QLabel("Priority:"), 0, 0)
        form_layout.addWidget(self.priority_combo, 0, 1)
        form_layout.addWidget(QLabel("Category:"), 1, 0)
        form_layout.addWidget(self.category_combo, 1, 1)
        form_layout.addWidget(QLabel("Due Date:"), 2, 0)
        form_layout.addWidget(self.due_date, 2, 1)
        
        add_btn = QPushButton("🎯 Add Task")
        add_btn.clicked.connect(self.add_task)
        
        add_task_layout.addWidget(QLabel("Title:"))
        add_task_layout.addWidget(self.title_input)
        add_task_layout.addWidget(QLabel("Description:"))
        add_task_layout.addWidget(self.desc_input)
        add_task_layout.addLayout(form_layout)
        add_task_layout.addWidget(add_btn)
        
        add_task_group.setLayout(add_task_layout)
        
        # Statistics section
        stats_group = QGroupBox("📊 Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel("Loading statistics...")
        self.stats_label.setWordWrap(True)
        self.stats_label.setStyleSheet("color: #ffffff; font-size: 12px; line-height: 1.4;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        stats_layout.addWidget(self.stats_label)
        stats_layout.addWidget(self.progress_bar)
        stats_group.setLayout(stats_layout)
        
        left_sidebar.addWidget(add_task_group)
        left_sidebar.addWidget(stats_group)
        left_sidebar.addStretch()
        
        # Right side - Task list
        right_side = QVBoxLayout()
        
        # Filter section
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search tasks...")
        self.search_input.textChanged.connect(self.filter_tasks)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Tasks", "⏳ Pending", "🔄 In Progress", "✅ Completed", "⚠️ Overdue"])
        
        clear_btn = QPushButton("🔄 Refresh")
        clear_btn.setObjectName("secondary")
        clear_btn.clicked.connect(self.load_tasks)
        
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addWidget(clear_btn)
        
        # Task list
        self.task_scroll = QScrollArea()
        self.task_scroll.setStyleSheet("background-color: #1e1e1e; border: none;")
        self.task_widget = QWidget()
        self.task_widget.setStyleSheet("background-color: #1e1e1e;")
        self.task_layout = QVBoxLayout()
        self.task_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.task_layout.setSpacing(10)
        self.task_widget.setLayout(self.task_layout)
        self.task_scroll.setWidget(self.task_widget)
        self.task_scroll.setWidgetResizable(True)
        
        right_side.addLayout(filter_layout)
        right_side.addWidget(QLabel("📋 Your Tasks:"))
        right_side.addWidget(self.task_scroll)
        
        # Add to main layout
        main_layout.addLayout(left_sidebar, 1)
        main_layout.addLayout(right_side, 2)
        
        self.update_statistics()

    def set_dark_palette(self):
        """Set dark palette for the entire application"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(76, 175, 80))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        
        QApplication.setPalette(dark_palette)

    def add_task(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Input Error", "Please enter a task title!")
            return
            
        description = self.desc_input.toPlainText().strip()
        priority = Priority(self.priority_combo.currentIndex() + 1)
        category = self.category_combo.currentText().replace("💼 ", "").replace("🏠 ", "").replace("🛒 ", "").replace("❤️ ", "").replace("📚 ", "")
        due_date = self.due_date.date().toPyDate()
        
        task = self.todo_list.add_task(title, description, priority, due_date, category)
        if task:
            self.add_task_to_ui(task)
            self.clear_inputs()
            self.update_statistics()
            QMessageBox.information(self, "Success", "Task added successfully! 🎉")
        else:
            QMessageBox.critical(self, "Error", "Failed to add task!")

    def clear_inputs(self):
        self.title_input.clear()
        self.desc_input.clear()
        self.priority_combo.setCurrentIndex(1)  # Medium
        self.due_date.setDate(QDate.currentDate().addDays(7))

    def add_task_to_ui(self, task):
        task_widget = TaskWidget(task)
        task_widget.taskUpdated.connect(self.on_task_updated)
        task_widget.taskDeleted.connect(self.delete_task)
        self.task_layout.addWidget(task_widget)

    def load_tasks(self):
        # Clear existing tasks
        for i in reversed(range(self.task_layout.count())): 
            widget = self.task_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
            
        # Add all tasks
        for task in self.todo_list.tasks:
            self.add_task_to_ui(task)
            
        self.update_statistics()

    def on_task_updated(self):
        self.todo_list.save_tasks()
        self.update_statistics()

    def delete_task(self, task_id):
        if self.todo_list.delete_task(task_id):
            self.load_tasks()
            QMessageBox.information(self, "Success", "Task deleted successfully!")
        else:
            QMessageBox.critical(self, "Error", "Failed to delete task!")

    def filter_tasks(self):
        search_text = self.search_input.text().lower()
        filter_text = self.filter_combo.currentText()
        
        for i in range(self.task_layout.count()):
            widget = self.task_layout.itemAt(i).widget()
            if widget:
                task = widget.task
                matches_search = (search_text in task.title.lower() or 
                                search_text in task.description.lower())
                
                matches_filter = True
                if filter_text == "⏳ Pending":
                    matches_filter = task.status == Status.PENDING
                elif filter_text == "🔄 In Progress":
                    matches_filter = task.status == Status.IN_PROGRESS
                elif filter_text == "✅ Completed":
                    matches_filter = task.status == Status.COMPLETED
                elif filter_text == "⚠️ Overdue":
                    matches_filter = task.is_overdue()
                
                widget.setVisible(matches_search and matches_filter)

    def update_statistics(self):
        stats = self.todo_list.get_statistics()
        
        stats_text = f"""
📈 Total Tasks: {stats['total']}
✅ Completed: {stats['completed']}
🔄 In Progress: {stats['in_progress']}
⏳ Pending: {stats['pending']}
⚠️ Overdue: {stats['overdue']}

🎯 Completion Rate: {stats['completion_rate']:.1f}%

Priority Breakdown:
🔵 Low: {stats['priority_stats'][Priority.LOW]}
🟡 Medium: {stats['priority_stats'][Priority.MEDIUM]}
🟠 High: {stats['priority_stats'][Priority.HIGH]}
🔴 Urgent: {stats['priority_stats'][Priority.URGENT]}
        """
        
        self.stats_label.setText(stats_text)
        self.progress_bar.setValue(int(stats['completion_rate']))
        self.progress_bar.setVisible(True)

def main():
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
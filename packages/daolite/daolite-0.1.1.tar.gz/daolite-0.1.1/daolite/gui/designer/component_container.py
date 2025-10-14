"""
ComponentContainer, ComputeBox, and GPUBox classes for the daolite pipeline designer.
"""

from typing import List, Optional

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QAction, QColorDialog, QGraphicsItem, QMenu

from daolite.compute import ComputeResources

from .component_block import ComponentBlock


class ComponentContainer(QGraphicsItem):
    """
    Base class for compute resource containers (CPU and GPU boxes).
    This class provides common functionality for containers that can hold
    component blocks and manage their layout.
    """

    def __init__(
        self, name: str, compute: Optional[ComputeResources] = None, z_value: int = -10
    ):
        super().__init__()
        self.name = name
        self.compute = compute
        self.child_items: List[QGraphicsItem] = []
        self.size = QRectF(0, 0, 250, 180)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(z_value)
        self._highlight = False  # Visual indicator for drag-over
        self.box_color = QColor(100, 150, 200)  # Default color - will be overridden
        self.fill_color = QColor(220, 230, 255, 70)
        self._resizing = False
        self._resize_edge = None  # Tracks which edge/corner is being resized
        self._edge_size = 8  # Size of the edge detection area for resizing
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.LeftButton)

    def set_theme(self, theme):
        self.theme = theme
        self.update()
        for child in self.childItems():
            if hasattr(child, "set_theme"):
                child.set_theme(theme)

    def set_highlight(self, value: bool):
        self._highlight = value
        self.update()

    def _update_all_transfer_indicators(self):
        if not self.scene():
            return
        from .connection import ComponentBlock, Connection

        blocks = [
            child for child in self.childItems() if isinstance(child, ComponentBlock)
        ]
        for item in self.scene().items():
            if isinstance(item, Connection):
                if item.start_block in blocks or item.end_block in blocks:
                    item.update_transfer_indicators()

    def contextMenuEvent(self, event):
        menu = QMenu()
        color_action = QAction("Set Color", menu)
        color_action.triggered.connect(self._on_set_color)
        menu.addAction(color_action)
        configure_action = QAction("Configure Resource", menu)
        configure_action.triggered.connect(self._on_configure)
        menu.addAction(configure_action)
        delete_action = QAction("Delete", menu)
        delete_action.triggered.connect(self._on_delete)
        menu.addAction(delete_action)
        menu.exec_(event.screenPos())

    def _on_set_color(self):
        color = QColorDialog.getColor(self.box_color)
        if color.isValid():
            self.box_color = color
            self.update()

    def _on_configure(self):
        if self.scene() and self.scene().parent():
            app = self.scene().parent()
            if hasattr(app, "_get_compute_resource"):
                app._get_compute_resource(self)

    def _on_delete(self):
        if self.scene():
            for child in list(self.childItems()):
                self.scene().removeItem(child)
            parent = self.parentItem()
            if parent and hasattr(parent, "child_items") and self in parent.child_items:
                parent.child_items.remove(self)
            self.scene().removeItem(self)

    def boundingRect(self) -> QRectF:
        return self.size.adjusted(
            -self._edge_size, -self._edge_size, self._edge_size, self._edge_size
        )

    def paint(self, painter: QPainter, option, widget):
        theme = getattr(self, "theme", getattr(self.scene(), "theme", "light"))
        is_dark = theme == "dark"
        if is_dark:
            if isinstance(self, ComputeBox):
                fill = QColor(60, 80, 120, 180)
                box = QColor(120, 180, 255)
            elif isinstance(self, GPUBox):
                fill = QColor(80, 120, 80, 180)
                box = QColor(180, 255, 180)
            else:
                fill = QColor(40, 50, 60, 180)
                box = self.box_color.lighter(180)
        else:
            fill = self.fill_color
            box = self.box_color.lighter(180)
        pen = QPen(box if is_dark else self.box_color, 2)
        if self._highlight:
            pen.setWidth(8)
        elif self.isSelected():
            pen.setWidth(4)
        painter.setPen(pen)
        painter.setBrush(QBrush(fill))
        painter.drawRoundedRect(self.size, 14, 14)

        # Create the title rect at the top of the container
        title_height = 25
        title_rect = QRectF(0, 0, self.size.width(), title_height)

        painter.setBrush(QBrush(box))
        painter.drawRoundedRect(title_rect, 12, 12)
        painter.setPen(Qt.black if not is_dark else QColor("#e0e6ef"))
        font = QFont("Arial", 9, QFont.Bold)
        painter.setFont(font)
        painter.drawText(title_rect, Qt.AlignCenter, self.name)
        if self.compute:
            compute_name = getattr(
                self.compute, "name", str(type(self.compute).__name__)
            )
            painter.setFont(QFont("Arial", 8))
            painter.setPen(Qt.black if not is_dark else QColor("#b3e1ff"))
            painter.drawText(10, 40, f"Resource: {compute_name}")

    def _get_edge_at_position(self, pos):
        """Determine which edge or corner the cursor is near."""
        left = pos.x() <= self._edge_size
        right = pos.x() >= self.size.width() - self._edge_size
        top = pos.y() <= self._edge_size
        bottom = pos.y() >= self.size.height() - self._edge_size

        # Corners first
        if top and left:
            return "top-left"
        elif top and right:
            return "top-right"
        elif bottom and left:
            return "bottom-left"
        elif bottom and right:
            return "bottom-right"
        # Then edges
        elif left:
            return "left"
        elif right:
            return "right"
        elif top:
            return "top"
        elif bottom:
            return "bottom"
        else:
            return None

    def hoverMoveEvent(self, event):
        """Change cursor shape when hovering near edges for resizing."""
        if self._resizing:
            return

        edge = self._get_edge_at_position(event.pos())

        # Set cursor based on which edge/corner we're hovering over
        if edge == "top-left" or edge == "bottom-right":
            self.setCursor(Qt.SizeFDiagCursor)
        elif edge == "top-right" or edge == "bottom-left":
            self.setCursor(Qt.SizeBDiagCursor)
        elif edge == "left" or edge == "right":
            self.setCursor(Qt.SizeHorCursor)
        elif edge == "top" or edge == "bottom":
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def hoverLeaveEvent(self, event):
        """Reset cursor when mouse leaves the container."""
        if not self._resizing:
            self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        edge = self._get_edge_at_position(event.pos())

        # If clicking on an edge, start resizing
        if edge:
            self._resizing = True
            self._resize_edge = edge
            self._resize_start = event.pos()
            self._orig_size = QRectF(self.size)
            self._orig_pos = self.pos()
            event.accept()
            return

        # Store the initial position for undo tracking
        self._initial_pos = self.pos()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing:
            # Calculate how much to resize based on the edge/corner being dragged
            dx = event.pos().x() - self._resize_start.x()
            dy = event.pos().y() - self._resize_start.y()

            # We'll always work with width and height directly
            # rather than rectangle coordinates
            old_width = self._orig_size.width()
            old_height = self._orig_size.height()
            new_width = old_width
            new_height = old_height
            new_pos = QPointF(self._orig_pos)

            # Handle horizontal resizing
            if "left" in self._resize_edge:
                # When resizing from left edge, adjust both position and width
                new_width = max(120, old_width - dx)  # Ensure minimum width
                # Move the container by the difference between old and new width
                new_pos.setX(self._orig_pos.x() - (new_width - old_width))
            elif "right" in self._resize_edge:
                new_width = max(120, old_width + dx)  # Ensure minimum width

            # Handle vertical resizing
            if "top" in self._resize_edge:
                # When resizing from top edge, adjust both position and height
                new_height = max(80, old_height - dy)  # Ensure minimum height
                # Move the container by the difference between old and new height
                new_pos.setY(self._orig_pos.y() - (new_height - old_height))
            elif "bottom" in self._resize_edge:
                new_height = max(80, old_height + dy)  # Ensure minimum height

            # Apply the resize boundaries
            new_width, new_height = self._check_resize_boundaries(new_width, new_height)

            # Create a new rectangle with the origin at (0,0)
            new_rect = QRectF(0, 0, new_width, new_height)

            # Update size and position
            self.prepareGeometryChange()
            self.size = new_rect
            self.setPos(new_pos)
            self.update()

            # Make sure children fit within the new bounds
            self.auto_arrange_children()
            self._update_all_transfer_indicators()

            event.accept()
            return

        # Handle constrained movement for GPUBox inside ComputeBox
        if isinstance(self, GPUBox) and self.parentItem():
            new_pos = self.pos() + event.pos() - event.lastPos()
            parent = self.parentItem()
            margin = 10
            min_x = margin
            min_y = margin
            max_x = parent.size.width() - self.size.width() - margin
            max_y = parent.size.height() - self.size.height() - margin
            constrained_x = max(min_x, min(max_x, new_pos.x()))
            constrained_y = max(min_y, min(max_y, new_pos.y()))
            if constrained_x != new_pos.x() or constrained_y != new_pos.y():
                self.setPos(constrained_x, constrained_y)
                event.accept()
                return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._resizing:
            self._resizing = False
            self._resize_edge = None
            self._update_all_transfer_indicators()
            event.accept()
            return

        # Handle undo tracking for movement if position changed
        if (
            hasattr(self, "_initial_pos")
            and self.pos() != self._initial_pos
            and self.scene()
            and hasattr(self.scene(), "parent")
        ):
            scene_parent = self.scene().parent()
            if hasattr(scene_parent, "undo_stack"):
                from .undo_stack import MoveComponentCommand

                command = MoveComponentCommand(self, self._initial_pos, self.pos())
                scene_parent.undo_stack.push(command)
                print(
                    f"[DEBUG] Created undo command for {type(self).__name__} movement"
                )

        super().mouseReleaseEvent(event)

    def add_child(self, item: QGraphicsItem):
        item.setParentItem(self)
        self.child_items.append(item)
        if hasattr(item, "compute"):
            item.compute = self.compute
        self.auto_arrange_children()

    def auto_arrange_children(self):
        if not self.child_items:
            return
        margin = 20
        changed = True
        max_iter = 30
        iter_count = 0

        def child_key(child):
            c_rect = child.mapToParent(child.boundingRect()).boundingRect()
            return (c_rect.top(), c_rect.left())

        while changed and iter_count < max_iter:
            changed = False
            sorted_children = sorted(self.child_items, key=child_key)
            child_rects = [
                child.mapToParent(child.boundingRect()).boundingRect()
                for child in sorted_children
            ]
            for i, rect1 in enumerate(child_rects):
                for j, rect2 in enumerate(child_rects):
                    if i == j:
                        continue
                    if rect1.intersects(rect2):
                        if child_key(sorted_children[j]) > child_key(
                            sorted_children[i]
                        ):
                            dx = rect1.right() - rect2.left() + 10
                            dy = rect1.bottom() - rect2.top() + 10
                            move_right = rect2.left() + dx <= self.size.width() - margin
                            move_down = rect2.top() + dy <= self.size.height() - margin
                            if move_right and (not move_down or dx <= dy):
                                sorted_children[j].setPos(
                                    sorted_children[j].x() + dx, sorted_children[j].y()
                                )
                            elif move_down:
                                sorted_children[j].setPos(
                                    sorted_children[j].x(), sorted_children[j].y() + dy
                                )
                            else:
                                sorted_children[j].setPos(
                                    sorted_children[j].x() + dx,
                                    sorted_children[j].y() + dy,
                                )
                            changed = True
                            break
                if changed:
                    break
            iter_count += 1
        for child in self.child_items:
            c_rect = child.mapToParent(child.boundingRect()).boundingRect()
            dx = dy = 0
            if c_rect.left() < 0:
                dx = -c_rect.left() + 10
            elif c_rect.right() > self.size.width():
                dx = self.size.width() - c_rect.right() - 10
            if c_rect.top() < 0:
                dy = -c_rect.top() + 10
            elif c_rect.bottom() > self.size.height():
                dy = self.size.height() - c_rect.bottom() - 10
            if dx != 0 or dy != 0:
                child.setPos(child.x() + dx, child.y() + dy)
        self._expand_for_children(margin)

    def _expand_for_children(self, margin=10):
        for child in self.child_items:
            c_rect = child.mapToParent(child.boundingRect()).boundingRect()
            expand_w = c_rect.right() + margin - self.size.width()
            expand_h = c_rect.bottom() + margin - self.size.height()
            if expand_w > 0 or expand_h > 0:
                new_width = max(self.size.width(), c_rect.right() + margin)
                new_height = max(self.size.height(), c_rect.bottom() + margin)
                new_width, new_height = self._check_resize_boundaries(
                    new_width, new_height
                )
                self.size = QRectF(0, 0, new_width, new_height)
                self.prepareGeometryChange()
                self.update()

    def snap_child_fully_inside(self, child):
        c_rect = child.mapToParent(child.boundingRect()).boundingRect()
        changed = False
        margin = 10
        if c_rect.right() > self.size.width():
            if c_rect.right() > self.size.width() + 20:
                child.setX(self.size.width() - c_rect.width() - margin)
                changed = True
            else:
                new_width = c_rect.right() + margin
                new_width, _ = self._check_resize_boundaries(
                    new_width, self.size.height()
                )
                self.size.setWidth(new_width)
                changed = True
        if c_rect.bottom() > self.size.height():
            if c_rect.bottom() > self.size.height() + 20:
                child.setY(self.size.height() - c_rect.height() - margin)
                changed = True
            else:
                new_height = c_rect.bottom() + margin
                _, new_height = self._check_resize_boundaries(
                    self.size.width(), new_height
                )
                self.size.setHeight(new_height)
                changed = True
        if c_rect.left() < 0:
            child.setX(margin)
            changed = True
        if c_rect.top() < 0:
            child.setY(margin)
            changed = True
        overlaps = False
        for sibling in self.childItems():
            if sibling is not child and isinstance(sibling, ComponentBlock):
                sibling_rect = sibling.mapToParent(
                    sibling.boundingRect()
                ).boundingRect()
                if c_rect.intersects(sibling_rect):
                    overlaps = True
                    break
        if overlaps:
            for sibling in self.childItems():
                if sibling is not child and isinstance(sibling, ComponentBlock):
                    sibling_rect = sibling.mapToParent(
                        sibling.boundingRect()
                    ).boundingRect()
                    if c_rect.intersects(sibling_rect):
                        dx = sibling_rect.right() - c_rect.left() + margin
                        dy = sibling_rect.bottom() - c_rect.top() + margin
                        if dx < dy:
                            child.setX(child.x() + dx)
                        else:
                            child.setY(child.y() + dy)
                        c_rect = child.mapToParent(child.boundingRect()).boundingRect()
                        changed = True
        if changed:
            self.prepareGeometryChange()
            self.update()

    def shape(self):
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def mouseDoubleClickEvent(self, event):
        title_rect = QRectF(0, 0, self.size.width(), 25)
        if title_rect.contains(event.pos()):
            # If double-clicking on the title, show rename dialog
            from .dialogs.misc_dialogs import StyledTextInputDialog

            dlg = StyledTextInputDialog(
                f"Rename {type(self).__name__}",
                "Enter new name:",
                self.name,
                self.scene().parent(),
            )
            if dlg.exec_():
                name = dlg.getText()
                self.name = name
                if self.scene():
                    self.scene().update()
            event.accept()
            return
        else:
            # If double-clicking elsewhere on the container, show resource dialog
            if self.scene() and self.scene().parent():
                app = self.scene().parent()
                if hasattr(app, "_get_compute_resource"):
                    app._get_compute_resource(self)
                    event.accept()
                    return

        super().mouseDoubleClickEvent(event)


class ComputeBox(ComponentContainer):
    """
    A compute box container representing a physical computer in the pipeline.
    Can contain components or GPU boxes as children.
    """

    def __init__(self, name="Computer", size=None, compute=None, cpu_resource=None):
        super().__init__(name, compute, z_value=-10)
        self.box_color = QColor(30, 70, 140)
        self.fill_color = QColor(220, 230, 240, 160)
        self.size = QRectF(0, 0, 320, 240) if size is None else size
        self.cpu_resource = cpu_resource
        self.child_items = []
        self.setAcceptHoverEvents(True)  # Enable hover events for tooltips

    def set_theme(self, theme):
        super().set_theme(theme)

    def _generate_detailed_tooltip(self) -> str:
        """Generate a detailed tooltip showing compute resource information."""
        tooltip = f"<b>{self.name}</b> (Compute Node)<br>"

        # Add compute resource information if available
        if self.compute:
            tooltip += "<b>Compute Resource:</b><br>"
            # Hardware type
            hardware_type = getattr(self.compute, "hardware", "CPU")
            tooltip += f"• Type: {hardware_type}<br>"

            # CPU-specific information
            if hasattr(self.compute, "cores"):
                tooltip += f"• Cores: {self.compute.cores}<br>"

            if hasattr(self.compute, "core_frequency"):
                freq = self.compute.core_frequency
                tooltip += f"• Core Frequency: {freq/1e9:.2f} GHz<br>"

            if hasattr(self.compute, "flops_per_cycle"):
                tooltip += f"• FLOPS per cycle: {self.compute.flops_per_cycle}<br>"

            # Performance metrics
            if hasattr(self.compute, "flops"):
                flops = self.compute.flops
                if flops >= 1e12:
                    tooltip += f"• Performance: {flops/1e12:.2f} TFLOPS<br>"
                else:
                    tooltip += f"• Performance: {flops/1e9:.2f} GFLOPS<br>"

            # Memory details
            if (
                hasattr(self.compute, "memory_channels")
                and hasattr(self.compute, "memory_width")
                and hasattr(self.compute, "memory_frequency")
            ):
                tooltip += f"• Memory channels: {self.compute.memory_channels}<br>"
                tooltip += f"• Memory width: {self.compute.memory_width} bits<br>"
                tooltip += f"• Memory frequency: {self.compute.memory_frequency/1e9:.2f} GHz<br>"

            if hasattr(self.compute, "memory_bandwidth"):
                mem_bw = (
                    self.compute.memory_bandwidth / 8
                )  # Convert from bits/s to bytes/s
                tooltip += f"• Memory Bandwidth: {mem_bw/1e9:.2f} GB/s<br>"

            # Network information
            if hasattr(self.compute, "network_speed"):
                net_speed = self.compute.network_speed
                tooltip += f"• Network Speed: {net_speed/1e9:.2f} Gbps<br>"

            # Driver overhead
            if hasattr(self.compute, "time_in_driver"):
                tooltip += f"• Driver Overhead: {self.compute.time_in_driver} μs<br>"

            # Attached GPUs
            if hasattr(self.compute, "attached_gpus") and self.compute.attached_gpus:
                tooltip += "<br><b>Attached GPUs:</b><br>"
                for i, gpu in enumerate(self.compute.attached_gpus):
                    name = getattr(gpu, "name", f"GPU {i+1}")
                    tooltip += f"• {name}<br>"

                    # Add GPU metrics if available
                    if hasattr(gpu, "flops"):
                        gpu_flops = gpu.flops
                        if gpu_flops >= 1e12:
                            tooltip += (
                                f"  - Performance: {gpu_flops/1e12:.2f} TFLOPS<br>"
                            )
                        else:
                            tooltip += (
                                f"  - Performance: {gpu_flops/1e9:.2f} GFLOPS<br>"
                            )

                    if hasattr(gpu, "memory_bandwidth"):
                        gpu_mem_bw = (
                            gpu.memory_bandwidth / 8
                        )  # Convert from bits/s to bytes/s
                        tooltip += (
                            f"  - Memory Bandwidth: {gpu_mem_bw/1e9:.2f} GB/s<br>"
                        )

        return tooltip

    def hoverEnterEvent(self, event):
        """Show detailed tooltip on hover."""
        self.setToolTip(self._generate_detailed_tooltip())
        super().hoverEnterEvent(event)

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        painter.setPen(QPen(QColor(70, 70, 70)))
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        if self.cpu_resource:
            painter.drawText(10, 50, f"CPU: {self.cpu_resource}")

    def _check_resize_boundaries(self, new_width, new_height):
        return new_width, new_height


class GPUBox(ComponentContainer):
    """
    A visual container for grouping components that share the same GPU resource.
    Can only be placed inside a ComputeBox.
    """

    def __init__(self, name: str, gpu_resource: Optional[ComputeResources] = None):
        super().__init__(name, gpu_resource, z_value=-5)
        self.box_color = QColor(120, 180, 70)
        self.fill_color = QColor(220, 255, 200, 80)
        self.gpu_resource = gpu_resource
        self.size = QRectF(0, 0, 220, 120)
        self.setAcceptHoverEvents(True)  # Enable hover events for tooltips

    def set_theme(self, theme):
        super().set_theme(theme)

    def _generate_detailed_tooltip(self) -> str:
        """Generate a detailed tooltip showing GPU resource information."""
        tooltip = f"<b>{self.name}</b> (GPU)<br>"

        # Add GPU resource information if available
        if self.gpu_resource:
            tooltip += "<b>GPU Resource:</b><br>"

            # Basic information
            gpu_name = getattr(self.gpu_resource, "name", "")
            if gpu_name:
                tooltip += f"• Name: {gpu_name}<br>"

            # Core information if available
            if hasattr(self.gpu_resource, "cores"):
                tooltip += f"• Compute Units: {self.gpu_resource.cores}<br>"

            if hasattr(self.gpu_resource, "core_frequency"):
                freq = self.gpu_resource.core_frequency
                tooltip += f"• Core Frequency: {freq/1e9:.2f} GHz<br>"

            # Performance metrics
            if hasattr(self.gpu_resource, "flops"):
                flops = self.gpu_resource.flops
                if flops >= 1e12:
                    tooltip += f"• Performance: {flops/1e12:.2f} TFLOPS<br>"
                else:
                    tooltip += f"• Performance: {flops/1e9:.2f} GFLOPS<br>"

            # Memory information
            if hasattr(self.gpu_resource, "memory_bandwidth"):
                mem_bw = (
                    self.gpu_resource.memory_bandwidth / 8
                )  # Convert from bits/s to bytes/s
                tooltip += f"• Memory Bandwidth: {mem_bw/1e9:.2f} GB/s<br>"

            # Detailed memory specs if available
            if hasattr(self.gpu_resource, "memory_channels"):
                tooltip += f"• Memory channels: {self.gpu_resource.memory_channels}<br>"

            if hasattr(self.gpu_resource, "memory_width"):
                tooltip += f"• Memory width: {self.gpu_resource.memory_width} bits<br>"

            if hasattr(self.gpu_resource, "memory_frequency"):
                mem_freq = self.gpu_resource.memory_frequency
                tooltip += f"• Memory frequency: {mem_freq/1e9:.2f} GHz<br>"

            # Connection information
            if hasattr(self.gpu_resource, "network_speed"):
                net_speed = self.gpu_resource.network_speed
                tooltip += f"• PCIe/NVLink Speed: {net_speed/1e9:.2f} Gbps<br>"

            # Driver overhead
            if hasattr(self.gpu_resource, "time_in_driver"):
                tooltip += (
                    f"• Driver Overhead: {self.gpu_resource.time_in_driver} μs<br>"
                )

            # Host computer info if available
            parent = self.parentItem()
            if parent and hasattr(parent, "name") and hasattr(parent, "compute"):
                tooltip += f"<br><b>Host Computer:</b> {parent.name}<br>"

                if hasattr(parent.compute, "network_speed"):
                    parent_net_speed = parent.compute.network_speed
                    tooltip += f"• Host Network: {parent_net_speed/1e9:.2f} Gbps<br>"

        return tooltip

    def hoverEnterEvent(self, event):
        """Show detailed tooltip on hover."""
        self.setToolTip(self._generate_detailed_tooltip())
        super().hoverEnterEvent(event)

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        theme = getattr(self, "theme", getattr(self.scene(), "theme", "light"))
        is_dark = theme == "dark"
        if self.gpu_resource:
            gpu_name = getattr(
                self.gpu_resource, "name", str(type(self.gpu_resource).__name__)
            )
            painter.setFont(QFont("Arial", 8))
            painter.setPen(Qt.black if not is_dark else QColor("#b3e1ff"))
            painter.drawText(10, 45, f"GPU: {gpu_name}")

    def _check_resize_boundaries(self, new_width, new_height):
        parent = self.parentItem()
        if parent and hasattr(parent, "size"):
            parent_size = parent.size
            max_width = parent_size.width() - self.pos().x() - 10
            max_height = parent_size.height() - self.pos().y() - 10
            new_width = min(new_width, max_width)
            new_height = min(new_height, max_height)
        return new_width, new_height

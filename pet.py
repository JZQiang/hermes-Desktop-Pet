#!/usr/bin/env python3
"""
Hermes Desktop Pet — 小黑猫 v5
Fix: outward-pointing ears, connected legs.
"""

import json, math, random, sys, threading, time, urllib.request
from PySide6.QtWidgets import QApplication, QWidget, QMenu
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QFont
import AppKit


# Force Qt window to float above everything on macOS
def _force_floating(widget):
    """Set native NSWindow level to float above all other windows."""
    try:
        for w in AppKit.NSApp().windows():
            if w.isVisible():
                w.setLevel_(AppKit.NSFloatingWindowLevel)
                w.setCollectionBehavior_(
                    w.collectionBehavior() |
                    AppKit.NSWindowCollectionBehaviorCanJoinAllSpaces |
                    AppKit.NSWindowCollectionBehaviorFullScreenAuxiliary
                )
                return True
    except Exception:
        pass
    return False

HERMES = "http://localhost:9119/api/status"
W, H = 180, 150


class S:
    WORK, SLEEP = 0, 1
    L = ["工作中", "休息中"]
    D = [(255, 100, 100), (150, 150, 150)]


class Cat(QWidget):
    def __init__(self):
        super().__init__()
        self.st = S.SLEEP
        self.bl = False
        self.bp = self.rp = self.bnc = self.eg = 0
        self.r = True
        self.vx = self.vy = 0.0
        self.tx = self.ty = None
        self.drag = False
        self.dp = QPointF()
        self._win()
        self._tmr()
        self._pol()

    def _win(self):
        self.setWindowTitle("小黑猫")
        self.setFixedSize(W, H)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, True)
        # Force floating after showing via timer
        QTimer.singleShot(200, lambda: _force_floating(self))
        QTimer.singleShot(1000, lambda: _force_floating(self))
    def _tmr(self):
        for fn, t in [(self._an, 33), (self._mv, 50)]:
            tm = QTimer(self); tm.timeout.connect(fn); tm.start(t)
        bt = QTimer(self)
        bt.timeout.connect(lambda: setattr(self, 'bl', True) or QTimer.singleShot(150, lambda: setattr(self, 'bl', False)))
        bt.start(2500)

    def _an(self):
        self.bp += 0.05
        sp = abs(self.vx) + abs(self.vy)
        if sp > 0.3:
            self.rp += sp * 0.12
            self.bnc = abs(math.sin(self.rp * 2)) * 3
            if abs(self.vx) > 0.1: self.r = self.vx > 0
        else:
            self.rp *= 0.9; self.bnc *= 0.9
        self.update()

    def _pk(self):
        g = QApplication.primaryScreen().availableGeometry()
        self.tx = random.uniform(30, g.width() - W - 30)
        self.ty = random.uniform(40, g.height() - H - 30)

    def _mv(self):
        g = QApplication.primaryScreen().availableGeometry()
        x, y = self.x(), self.y()
        if self.st != S.WORK:
            self.vx *= 0.8; self.vy *= 0.8
            return
        if self.tx is None: self._pk()
        sp, pl = 5.0, 0.015
        self.vx += (self.tx - x) * pl + random.uniform(-0.2, 0.2)
        self.vy += (self.ty - y) * pl + random.uniform(-0.2, 0.2)
        if abs(x - self.tx) < 40 and abs(y - self.ty) < 40: self.tx = None
        self.vx *= 0.95; self.vy *= 0.95
        s = math.hypot(self.vx, self.vy)
        if s > sp: self.vx, self.vy = self.vx / s * sp, self.vy / s * sp
        nx, ny = x + self.vx, y + self.vy
        if nx < 0: nx = 0; self.vx = abs(self.vx) * 0.7; self.tx = None
        if nx > g.width() - W: nx = g.width() - W; self.vx = -abs(self.vx) * 0.7; self.tx = None
        if ny < 20: ny = 20; self.vy = abs(self.vy) * 0.7; self.ty = None
        if ny > g.height() - H: ny = g.height() - H; self.vy = -abs(self.vy) * 0.7; self.ty = None
        self.move(int(nx), int(ny))

    def _pol(self):
        def p():
            while True:
                try:
                    with urllib.request.urlopen(HERMES, timeout=3) as r:
                        d = json.loads(r.read())
                    gw = d.get("gateway_state", ""); se = d.get("active_sessions", 0)
                    self.st = S.WORK if (gw == "running" and se > 0) else S.SLEEP
                except: self.st = S.SLEEP
                time.sleep(2)
        threading.Thread(target=p, daemon=True).start()

    # ─── DRAW ────────────────────────────────────────────────────────

    C = QColor(22, 22, 26)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        br = math.sin(self.bp) * 1.5
        cy = H / 2 + 5 + br + self.bnc
        sp = abs(self.vx) + abs(self.vy)
        run = sp > 0.3
        slp = self.st != S.WORK
        d = 1 if self.r else -1

        bx, by = W / 2 + d * 5, cy
        bw, bh = 48, 32

        p.setPen(Qt.PenStyle.NoPen)

        # ═══ TAIL (behind body) ═══
        tx0 = bx - d * 26
        ty0 = by - 4
        t = QPainterPath()
        t.moveTo(tx0, ty0)
        t.cubicTo(tx0 - d * 26, ty0 - 4, tx0 - d * 34, ty0 - 26, tx0 - d * 24, ty0 - 36)
        pen = QPen(self.C, 4.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(t)
        p.setPen(Qt.PenStyle.NoPen)

        # ═══ LEGS (drawn BEFORE body so body overlaps them) ═══
        lw, lh = 6, 12
        if run:
            rp = self.rp
            leg_positions = [(-15, 0), (-6, math.pi), (6, math.pi / 2), (15, math.pi * 1.5)]
            for ox, phase in leg_positions:
                swing = math.sin(rp + phase) * 8
                lx = bx + ox
                ly = by + bh / 2 - 2  # start slightly INSIDE body
                p.save()
                p.translate(lx, ly)
                p.rotate(swing * 2)
                p.setBrush(self.C)
                # Leg body
                leg_h = lh + max(0, swing)
                p.drawRoundedRect(QRectF(-3, 0, 6, leg_h), 2, 2)
                # Paw
                p.drawRoundedRect(QRectF(-3.5, leg_h - 2, 8, 5), 2, 2)
                p.restore()
        elif slp:
            for ox in (-14, -4, 5, 15):
                p.drawRoundedRect(QRectF(bx + ox - 3, by + bh / 2 - 4, 7, 9), 3, 3)
                p.drawRoundedRect(QRectF(bx + ox - 3.5, by + bh / 2 + 4, 8, 4), 2, 2)
        else:
            for ox in (-15, -6, 6, 15):
                p.drawRoundedRect(QRectF(bx + ox - 3, by + bh / 2 - 2, 6, lh), 2, 2)
                p.drawRoundedRect(QRectF(bx + ox - 3.5, by + bh / 2 + lh - 3, 8, 5), 2, 2)

        # ═══ BODY ═══
        p.setBrush(self.C)
        p.drawEllipse(QRectF(bx - bw / 2, by - bh / 2, bw, bh))

        # ═══ HEAD ═══
        hx = bx + d * 26
        hy = by - 10 + br
        hr = 28
        p.drawEllipse(QPointF(hx, hy), hr, hr)

        # ═══ EARS — thick, rounded, curved tips ═══
        for s, tilt in [(-1, -15), (1, 15)]:
            base_y = hy - hr * 0.6
            base_l = hx + s * hr * 0.0
            base_r = hx + s * hr * 0.65
            tip_x = base_r + s * math.sin(math.radians(tilt)) * 18
            tip_y = base_y - math.cos(math.radians(tilt)) * 18 - 2
            # Curved ear with rounded tip
            ep = QPainterPath()
            ep.moveTo(base_l, base_y)
            ep.cubicTo(base_l + s * 2, base_y - 10,
                       tip_x - s * 3, tip_y + 4,
                       tip_x, tip_y)
            ep.cubicTo(tip_x + s * 3, tip_y + 4,
                       base_r - s * 2, base_y - 10,
                       base_r, base_y)
            ep.closeSubpath()
            p.setBrush(self.C)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawPath(ep)
            # Pink inner — smaller curved ear
            ip = QPainterPath()
            ip.moveTo(base_l + s * 6, base_y - 2)
            ip.cubicTo(base_l + s * 6, base_y - 8,
                       tip_x - s * 1, tip_y + 6,
                       tip_x * 0.85 + hx * 0.15, tip_y + 5)
            ip.cubicTo(tip_x * 0.85 + hx * 0.15, tip_y + 5,
                       base_r - s * 4, base_y - 8,
                       base_r - s * 4, base_y - 2)
            ip.closeSubpath()
            p.setBrush(QColor(255, 120, 120, 150))
            p.drawPath(ip)

        # ═══ EYES (BOTH, same size) ═══
        if slp:
            pen = QPen(QColor(180, 180, 190), 2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
            for side in (-0.35, 0.35):
                ex = hx + side * hr * 1.1
                ey = hy - 2
                p.drawLine(int(ex - 5), int(ey), int(ex + 5), int(ey))
            p.setPen(Qt.PenStyle.NoPen)
        elif self.bl:
            pen = QPen(QColor(180, 180, 190), 2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
            for side in (-0.35, 0.35):
                ex = hx + side * hr * 1.1
                ey = hy - 2
                p.drawLine(int(ex - 5), int(ey), int(ex + 5), int(ey))
            p.setPen(Qt.PenStyle.NoPen)
        else:
            gl = 1.0
            for side in (-0.35, 0.35):
                ex = hx + side * hr * 1.1
                ey = hy - 2
                ew, eh = 12, 11
                # Sclera
                scl = QColor(int(200 * gl), int(230 * gl), int(80 + 40 * gl))
                p.setBrush(scl); p.setPen(QPen(QColor(30, 30, 36), 1))
                p.drawEllipse(QRectF(ex - ew / 2, ey - eh / 2, ew, eh))
                # Pupil
                p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(6, 6, 10))
                p.drawEllipse(QRectF(ex - 2, ey - 3, 4, 6))
                # Highlight
                p.setBrush(QColor(255, 255, 255, 230))
                p.drawEllipse(QPointF(ex - 2, ey - 2), 2, 2)

        # ═══ SNOUT (centered between eyes) ═══
        sx = hx
        sy = hy + 8
        p.setBrush(QColor(255, 105, 105)); p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(sx, sy), 2.5, 2)

        # ═══ MOUTH + TEETH ═══
        if not slp:
            # Closed mouth — small curve
            p.setPen(QPen(QColor(200, 200, 210), 1.2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            mp = QPainterPath()
            mp.moveTo(sx - 4, sy + 5)
            mp.quadTo(sx, sy + 7, sx + 4, sy + 5)
            p.drawPath(mp)
            # Two fangs below the mouth, one each side
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(240, 240, 250))
            for dx in (-4, 4):
                f = QPainterPath()
                f.moveTo(sx + dx - 1.5, sy + 5)
                f.lineTo(sx + dx + 1.5, sy + 5)
                f.lineTo(sx + dx, sy + 10)
                f.closeSubpath()
                p.drawPath(f)

        # ═══ WHISKERS — simple, short ═══
        p.setPen(QPen(QColor(140, 140, 150), 0.7))
        wx = sx + d * 2
        wy = sy + 2
        # Two whiskers per side, one up one down
        for ang, ln in [(-15, 12), (15, 12)]:
            rad = math.radians(ang)
            p.drawLine(int(wx), int(wy),
                       int(wx + d * math.cos(rad) * ln),
                       int(wy + math.sin(rad) * ln))

        # ═══ Zzz ═══
        if slp:
            zz = math.sin(time.time() * 3)
            zx = hx + d * 18
            for i, (dx, dy, sz) in enumerate([(12, -16, 9), (24, -30, 11), (38, -44, 14)]):
                f = QFont("STHeiti", sz); p.setFont(f)
                p.setPen(QPen(QColor(130, 130, 190, 180), 1.5))
                p.drawText(QPointF(zx + dx * d, hy + dy + zz * i * 3), "z" if i < 2 else "Z")

        # ═══ STATUS DOT ═══
        r, g, b = S.D[self.st]
        p.setBrush(QColor(r, g, b))
        p.drawEllipse(QPointF(W / 2, 12), 3.5, 3.5)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.drag = True
            self.dp = e.globalPosition() - QPointF(self.frameGeometry().x(), self.frameGeometry().y())
            self.vx = self.vy = 0; self.tx = None

    def mouseMoveEvent(self, e):
        if self.drag: self.move((e.globalPosition() - self.dp).toPoint())

    def mouseReleaseEvent(self, e): self.drag = False

    def contextMenuEvent(self, e):
        m = QMenu(self)
        st = m.addAction(f"🐱 {S.L[self.st]}"); st.setEnabled(False)
        m.addSeparator()
        at = m.addAction("📌 置顶"); at.setCheckable(True); at.setChecked(True)
        at.triggered.connect(self._tp)
        m.addSeparator()
        qa = m.addAction("❌ 退出")
        ra = m.exec(e.globalPos())
        if ra == qa: QApplication.instance().quit()

    def _tp(self, c):
        self.hide()
        f = self.windowFlags()
        self.setWindowFlags(f | Qt.WindowType.WindowStaysOnTopHint if c else f & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        if c:
            QTimer.singleShot(200, lambda: _force_floating(self))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("小黑猫")
    pet = Cat()
    g = QApplication.primaryScreen().availableGeometry()
    pet.move(g.width() - W - 40, g.height() - H - 60)
    pet.show()
    sys.exit(app.exec())

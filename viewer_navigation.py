class ViewerNavigationMixin:
    """Миксин для управления прокруткой левой панели."""

    def scroll_to_top(self):
        self.scroll.verticalScrollBar().setValue(0)

    def scroll_page_up(self):
        sb = self.scroll.verticalScrollBar()
        sb.setValue(sb.value() - sb.pageStep())

    def scroll_page_down(self):
        sb = self.scroll.verticalScrollBar()
        sb.setValue(sb.value() + sb.pageStep())

    def scroll_to_bottom(self):
        sb = self.scroll.verticalScrollBar()
        sb.setValue(sb.maximum())

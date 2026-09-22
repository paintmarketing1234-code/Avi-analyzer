__version__ = "1.0.0"
from collections import defaultdict

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView


# ==========================================
# SETTINGS
# ==========================================

WINDOW = 5

# Minimum total historical rounds
MIN_DATA = 30

# Minimum matching occurrences of current pattern
MIN_SAMPLES = 10

# Statistical threshold
STOP_CONFIDENCE = 95.0


class AviatorApp(App):

    def build(self):

        self.results = []
        self.satisfied = False

        root = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(7)
        )

        # ==========================================
        # TITLE
        # ==========================================

        root.add_widget(
            Label(
                text="AVIATOR PATTERN ANALYZER",
                font_size=dp(22),
                bold=True,
                size_hint_y=None,
                height=dp(50)
            )
        )

        root.add_widget(
            Label(
                text="Historical statistical analysis only",
                font_size=dp(12),
                size_hint_y=None,
                height=dp(30)
            )
        )

        # ==========================================
        # INPUT
        # ==========================================

        input_row = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(5)
        )

        self.input_box = TextInput(
            hint_text="Enter result: 2.35x",
            multiline=False,
            font_size=dp(18)
        )

        self.add_button = Button(
            text="ADD"
        )

        self.add_button.bind(
            on_press=self.add_result
        )

        input_row.add_widget(
            self.input_box
        )

        input_row.add_widget(
            self.add_button
        )

        root.add_widget(
            input_row
        )

        # ==========================================
        # RESET
        # ==========================================

        reset_button = Button(
            text="RESET",
            size_hint_y=None,
            height=dp(45)
        )

        reset_button.bind(
            on_press=self.reset
        )

        root.add_widget(
            reset_button
        )

        # ==========================================
        # STATISTICS
        # ==========================================

        self.stats = Label(
            text=(
                "Rounds: 0\n"
                ">2x: 0 | <2x: 0"
            ),
            size_hint_y=None,
            height=dp(60)
        )

        root.add_widget(
            self.stats
        )

        # ==========================================
        # CURRENT PATTERN
        # ==========================================

        self.pattern = Label(
            text="Current pattern: --",
            size_hint_y=None,
            height=dp(40)
        )

        root.add_widget(
            self.pattern
        )

        # ==========================================
        # ANALYSIS
        # ==========================================

        self.analysis = Label(
            text="Analysis: Waiting...",
            size_hint_y=None,
            height=dp(65)
        )

        root.add_widget(
            self.analysis
        )

        # ==========================================
        # RESULT PANEL
        # ==========================================

        self.result_panel = Label(
            text=(
                "PROGRAM STATUS\n"
                "WAITING FOR DATA"
            ),
            font_size=dp(20),
            bold=True,
            size_hint_y=None,
            height=dp(100)
        )

        root.add_widget(
            self.result_panel
        )

        # ==========================================
        # STATUS
        # ==========================================

        self.status = Label(
            text="Enter previous results.",
            size_hint_y=None,
            height=dp(45)
        )

        root.add_widget(
            self.status
        )

        # ==========================================
        # HISTORY
        # ==========================================

        root.add_widget(
            Label(
                text="PREVIOUS RESULTS",
                bold=True,
                size_hint_y=None,
                height=dp(35)
            )
        )

        scroll = ScrollView()

        self.history = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(2)
        )

        self.history.bind(
            minimum_height=self.history.setter(
                "height"
            )
        )

        scroll.add_widget(
            self.history
        )

        root.add_widget(
            scroll
        )

        return root

    # ==================================================
    # ADD RESULT
    # ==================================================

    def add_result(self, instance):

        # If satisfied, don't accept more input
        if self.satisfied:
            return

        text = self.input_box.text.strip()

        if not text:

            self.status.text = (
                "Please enter a multiplier."
            )

            return

        try:

            value = float(
                text.lower().replace("x", "")
            )

            if value <= 0:
                raise ValueError

        except ValueError:

            self.status.text = (
                "Invalid value. Example: 2.35x"
            )

            return

        # Add result
        self.results.append(value)

        # Clear input
        self.input_box.text = ""

        # Update
        self.update_screen()

    # ==================================================
    # PATTERN ANALYSIS
    # ==================================================

    def analyze_pattern(self):

        if len(self.results) < MIN_DATA:
            return None

        patterns = defaultdict(
            lambda: [0, 0]
        )

        # Build historical relationships
        for i in range(
            WINDOW,
            len(self.results)
        ):

            previous_pattern = tuple(
                value > 2
                for value in self.results[
                    i - WINDOW:i
                ]
            )

            next_is_above_2 = (
                self.results[i] > 2
            )

            # Total times pattern occurred
            patterns[
                previous_pattern
            ][1] += 1

            # Times next result was >2x
            if next_is_above_2:

                patterns[
                    previous_pattern
                ][0] += 1

        # Current pattern
        current_pattern = tuple(
            value > 2
            for value in self.results[
                -WINDOW:
            ]
        )

        if current_pattern not in patterns:

            return None

        above_2, total = patterns[
            current_pattern
        ]

        if total == 0:
            return None

        confidence = (
            above_2 / total
        ) * 100

        return (
            confidence,
            total,
            above_2,
            current_pattern
        )

    # ==================================================
    # UPDATE SCREEN
    # ==================================================

    def update_screen(self):

        total = len(self.results)

        above_2 = sum(
            value > 2
            for value in self.results
        )

        below_2 = (
            total - above_2
        )

        # ------------------------------------------
        # GENERAL STATISTICS
        # ------------------------------------------

        if total > 0:

            historical_rate = (
                above_2 / total
            ) * 100

        else:

            historical_rate = 0

        self.stats.text = (
            f"Rounds: {total}\n"
            f">2x: {above_2} | "
            f"<2x: {below_2}\n"
            f"Historical >2x: "
            f"{historical_rate:.2f}%"
        )

        # ------------------------------------------
        # CURRENT PATTERN
        # ------------------------------------------

        if total >= WINDOW:

            current = self.results[
                -WINDOW:
            ]

            pattern_text = ""

            for value in current:

                if value > 2:
                    pattern_text += "H"
                else:
                    pattern_text += "L"

            self.pattern.text = (
                f"Current pattern: "
                f"{pattern_text}"
            )

        else:

            self.pattern.text = (
                "Current pattern: "
                "Need 5 rounds"
            )

        # ------------------------------------------
        # ANALYSIS
        # ------------------------------------------

        result = self.analyze_pattern()

        if result is None:

            remaining = max(
                0,
                MIN_DATA - total
            )

            self.analysis.text = (
                "Pattern analysis unavailable.\n"
                f"Need approximately "
                f"{remaining} more rounds."
            )

            self.result_panel.text = (
                "PROGRAM STATUS\n"
                "COLLECTING DATA"
            )

            self.status.text = (
                "Waiting for enough "
                "historical relationships."
            )

            self.update_history()

            return

        confidence, samples, above_count, pattern = (
            result
        )

        # ------------------------------------------
        # SHOW ANALYSIS
        # ------------------------------------------

        self.analysis.text = (
            f"Pattern confidence: "
            f"{confidence:.2f}%\n"
            f"Matching samples: {samples}\n"
            f">2x matches: {above_count}"
        )

        # ------------------------------------------
        # SATISFIED CONDITION
        # ------------------------------------------

        if (
            confidence >= STOP_CONFIDENCE
            and samples >= MIN_SAMPLES
        ):

            self.satisfied = True

            self.result_panel.text = (
                "✓ SATISFIED\n"
                "STATISTICAL ESTIMATE\n"
                "NEXT RESULT: ABOVE 2X"
            )

            self.status.text = (
                "Analysis threshold reached. "
                "Program stopped accepting input."
            )

            # Disable ADD
            self.add_button.disabled = True

        else:

            self.result_panel.text = (
                "PROGRAM STATUS\n"
                "ANALYZING..."
            )

            self.status.text = (
                "Threshold not reached. "
                "Continue entering results."
            )

        self.update_history()

    # ==================================================
    # HISTORY
    # ==================================================

    def update_history(self):

        self.history.clear_widgets()

        for number, value in enumerate(
            self.results,
            start=1
        ):

            label = Label(
                text=f"{number}. {value:.2f}x",
                size_hint_y=None,
                height=dp(32)
            )

            self.history.add_widget(
                label
            )

    # ==================================================
    # RESET
    # ==================================================

    def reset(self, instance):

        self.results = []

        self.satisfied = False

        self.add_button.disabled = False

        self.input_box.text = ""

        self.stats.text = (
            "Rounds: 0\n"
            ">2x: 0 | <2x: 0"
        )

        self.pattern.text = (
            "Current pattern: --"
        )

        self.analysis.text = (
            "Analysis: Waiting..."
        )

        self.result_panel.text = (
            "PROGRAM STATUS\n"
            "WAITING FOR DATA"
        )

        self.status.text = (
            "Enter previous results."
        )

        self.history.clear_widgets()


if __name__ == "__main__":
    AviatorApp().run()

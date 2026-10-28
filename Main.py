import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import json
import random


class DeutschTrainerApp:
    def __init__(self, root):
        self.root = root
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root.title("Deutsch Trainer")
        self.root.geometry("800x700")

        self.words_data = []
        self.sentences_data = []
        self._load_data()

        self.current_word_index = 0
        self.quiz_words = []
        self.flashcard_pool = []
        self.quiz_correct_answers = 0
        self.correct_answer_text = ""

        self.sentence_words = []
        self.sentence_labels = []
        self.current_sentence = {}
        self.create_widgets()

    def _load_data(self):
        try:
            with open("words.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                if 'words' in data:
                    for item in data['words']:
                        self.words_data.append(self._normalize_word(item))
                if 'sentences' in data:
                    self.sentences_data = data['sentences']
        except FileNotFoundError:
            self.words_data = [{"word": "der Hund", "translation": "собака", "article": "der"}]
            self.sentences_data = []
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Файл words.json поврежден. Проверьте его синтаксис.")
            self.root.destroy()
            return

    def _normalize_word(self, item):
        return {
            "word": item.get("deutsch"),
            "translation": item.get("russian"),
            "article": item.get("article", "")
        }

    def create_widgets(self):
        self.color_primary = "#FF8C42"
        self.color_primary_hover = "#E67E22"
        self.color_red = "#E74C3C"
        self.color_dark = "#1E1E1E"
        self.color_bg = "#111111"

        self.menu_container = ctk.CTkFrame(master=self.root, corner_radius=12, border_width=3, fg_color=self.color_dark,
                                           border_color=self.color_primary)
        self.menu_container.pack(expand=True, fill="both", padx=30, pady=30)

        title_label = ctk.CTkLabel(master=self.menu_container, text="Deutsch Trainer",
                                   font=ctk.CTkFont(family="Ebbe", size=64, weight="bold"), text_color="white")
        title_label.pack(pady=(40, 30))

        btn_cfg = {"width": 320, "height": 60, "font": ctk.CTkFont(family="Ebbe", size=20), "corner_radius": 12,
                   "text_color": "white", "hover_color": self.color_primary_hover, "fg_color": self.color_primary}

        self.btn_flashcards = ctk.CTkButton(master=self.menu_container, text="Карточки слов",
                                            command=self.start_flashcards, **btn_cfg)
        self.btn_flashcards.pack(pady=12)
        self.btn_quiz = ctk.CTkButton(master=self.menu_container, text="Викторина", command=self.start_quiz, **btn_cfg)
        self.btn_quiz.pack(pady=12)
        self.btn_sentence = ctk.CTkButton(master=self.menu_container, text="Составь предложение",
                                          command=self.start_sentence_game, **btn_cfg)
        self.btn_sentence.pack(pady=12)
        self.btn_grammar = ctk.CTkButton(master=self.menu_container, text="Справочник: Артикли",
                                         command=self.show_grammar, **btn_cfg)
        self.btn_grammar.pack(pady=12)
        self.btn_dictionary = ctk.CTkButton(master=self.menu_container, text="Словарь", command=self.show_dictionary,
                                            **btn_cfg)
        self.btn_dictionary.pack(pady=12)

        # --- ФРЕЙМ: КАРТОЧКИ СЛОВ ---
        self.flashcard_frame = ctk.CTkFrame(master=self.root, fg_color=self.color_bg)
        self.word_label = ctk.CTkLabel(master=self.flashcard_frame, text="",
                                       font=ctk.CTkFont(family="Ebbe", size=96, weight="bold"), text_color="white")
        self.word_label.pack(pady=80)
        self.translation_label = ctk.CTkLabel(master=self.flashcard_frame, text="",
                                              font=ctk.CTkFont(family="Ebbe", size=40), text_color="#FFCC99")
        self.translation_label.pack()
        fc_buttons_frame = ctk.CTkFrame(master=self.flashcard_frame, fg_color=self.color_bg)
        fc_buttons_frame.pack(pady=50)
        btn_fc_cfg = {"width": 140, "height": 50, "fg_color": "#444444", "hover_color": "#555555",
                      "text_color": "white", "corner_radius": 12, "font": ctk.CTkFont(family="Ebbe", size=18)}
        self.btn_show_translation = ctk.CTkButton(master=fc_buttons_frame, text="Перевод",
                                                  command=self.show_translation, **btn_fc_cfg)
        self.btn_show_translation.pack(side="left", padx=15)
        self.btn_next_card = ctk.CTkButton(master=fc_buttons_frame, text="Дальше", command=self.next_flashcard,
                                           **btn_fc_cfg)
        self.btn_next_card.pack(side="left", padx=15)
        self.btn_back_from_flashcards = ctk.CTkButton(master=fc_buttons_frame, text="← В меню",
                                                      command=self.show_main_menu, width=110, height=50,
                                                      fg_color=self.color_primary, hover_color=self.color_primary_hover,
                                                      text_color="white", corner_radius=12,
                                                      font=ctk.CTkFont(family="Ebbe", size=16))
        self.btn_back_from_flashcards.pack(side="left", padx=15)

        # --- ФРЕЙМ: ВИКТОРИНА ---
        self.quiz_frame = ctk.CTkFrame(master=self.root, fg_color=self.color_bg)
        self.quiz_word_label = ctk.CTkLabel(master=self.quiz_frame, text="", font=ctk.CTkFont(family="Ebbe", size=48),
                                            text_color="white")
        self.quiz_word_label.pack(pady=60)
        quiz_buttons_frame = ctk.CTkFrame(master=self.quiz_frame, fg_color=self.color_bg)
        quiz_buttons_frame.pack(pady=20)
        self.quiz_buttons = []
        for i in range(4):
            btn = ctk.CTkButton(master=quiz_buttons_frame, text="", command=lambda idx=i: self.check_quiz_answer(idx),
                                width=400, height=50, font=ctk.CTkFont(family="Ebbe", size=18), fg_color="#444444",
                                hover_color="#555555", text_color="white", corner_radius=10)
            btn.pack(pady=8, fill="x", padx=40)
            self.quiz_buttons.append(btn)

        self.btn_back_from_quiz = ctk.CTkButton(master=self.quiz_frame, text="← В меню", command=self.show_main_menu,
                                                width=240, fg_color=self.color_primary,
                                                hover_color=self.color_primary_hover,
                                                text_color="white", corner_radius=12,
                                                font=ctk.CTkFont(family="Ebbe", size=18))
        self.btn_back_from_quiz.pack(pady=30)

        # --- ФРЕЙМ: СОСТАВЬ ПРЕДЛОЖЕНИЕ ---
        self.sentence_frame = ctk.CTkFrame(master=self.root, fg_color=self.color_bg)
        self.sentence_target_label = ctk.CTkLabel(master=self.sentence_frame, text="Соберите предложение:",
                                                  font=ctk.CTkFont(family="Ebbe", size=24), text_color="white")
        self.sentence_target_label.pack(pady=20)
        self.sentence_container = ctk.CTkFrame(master=self.sentence_frame, fg_color="#222222")
        self.sentence_container.pack(pady=20, padx=40)
        sentence_actions_frame = ctk.CTkFrame(master=self.sentence_frame, fg_color=self.color_bg)
        sentence_actions_frame.pack(pady=20)
        self.btn_check_sentence = ctk.CTkButton(master=sentence_actions_frame, text="Проверить",
                                                command=self.check_sentence, font=ctk.CTkFont(family="Ebbe", size=18),
                                                fg_color=self.color_primary, hover_color=self.color_primary_hover,
                                                text_color="white", width=160)
        self.btn_check_sentence.pack(side="left", padx=20)
        self.btn_undo = ctk.CTkButton(master=sentence_actions_frame, text="↩ Отмена",
                                      command=self._undo_last_word, font=ctk.CTkFont(family="Ebbe", size=18),
                                      fg_color="#444444", hover_color="#555555", text_color="white", width=160)
        self.btn_undo.pack(side="left", padx=20)
        self.btn_next_sentence = ctk.CTkButton(master=self.sentence_frame, text="Следующее",
                                               command=self.start_sentence_game,
                                               font=ctk.CTkFont(family="Ebbe", size=18), fg_color="#444444",
                                               hover_color="#555555", text_color="white", width=200)
        self.btn_next_sentence.pack(pady=10)
        self.btn_back_from_sentence = ctk.CTkButton(master=self.sentence_frame, text="← В меню",
                                                    command=self.show_main_menu, width=240, fg_color=self.color_primary,
                                                    hover_color=self.color_primary_hover, text_color="white",
                                                    corner_radius=12, font=ctk.CTkFont(family="Ebbe", size=18))
        self.btn_back_from_sentence.pack(pady=20)

        # --- ФРЕЙМЫ: ГРАММАТИКА И СЛОВАРЬ ---
        self.grammar_frame = ctk.CTkFrame(master=self.root, fg_color=self.color_bg)
        txt = "Артикли в немецком языке:\n\nder — мужской род (Maskulinum)\ndie — женский род (Femininum)\ndas — средний род (Neutrum)"
        lbl = ctk.CTkLabel(self.grammar_frame, text=txt, font=ctk.CTkFont(family="Ebbe", size=20), justify="left",
                           text_color="white")
        lbl.pack(pady=60, padx=40)
        btn_grammar_back = ctk.CTkButton(self.grammar_frame, text="← В меню", command=self.show_main_menu,
                                         fg_color=self.color_primary, hover_color=self.color_primary_hover,
                                         text_color="white", corner_radius=12, font=ctk.CTkFont(family="Ebbe", size=18))
        btn_grammar_back.pack(pady=30)

        self.dict_frame = ctk.CTkFrame(master=self.root, fg_color=self.color_bg)
        self.dict_textbox = ctk.CTkTextbox(self.dict_frame, width=600, height=400,
                                           font=ctk.CTkFont(family="Ebbe", size=16), state="normal")
        self.dict_textbox.pack(pady=30, padx=40)
        self.dict_textbox.configure(state="disabled")
        btn_dict_back = ctk.CTkButton(self.dict_frame, text="← В меню", command=self.show_main_menu,
                                      fg_color=self.color_primary, hover_color=self.color_primary_hover,
                                      text_color="white", corner_radius=12, font=ctk.CTkFont(family="Ebbe", size=18))
        btn_dict_back.pack(pady=20)

    def hide_all_frames(self):
        for frame in [self.menu_container, self.flashcard_frame, self.quiz_frame, self.sentence_frame,
                      self.grammar_frame, self.dict_frame]:
            frame.pack_forget()

    def show_main_menu(self):
        self.hide_all_frames()
        self.menu_container.pack(expand=True, fill="both", padx=30, pady=30)

    # --- ЛОГИКА КАРТОЧЕК ---
    def start_flashcards(self):
        if not self.words_data:
            messagebox.showwarning("Внимание", "Словарь пуст!")
            return
        self.hide_all_frames()
        self.flashcard_frame.pack(expand=True, fill="both")
        self.flashcard_pool = self.words_data.copy()
        random.shuffle(self.flashcard_pool)
        self.current_word_index = 0
        self.show_current_flashcard()

    def show_current_flashcard(self):
        if not self.flashcard_pool:
            self.word_label.configure(text="Словарь пуст")
            return
        word_info = self.flashcard_pool[self.current_word_index]
        self.word_label.configure(text=word_info["word"])
        self.translation_label.configure(text="")

    def show_translation(self):
        if not self.flashcard_pool:
            return
        word_info = self.flashcard_pool[self.current_word_index]
        self.translation_label.configure(text=word_info["translation"])

    def next_flashcard(self):
        if not self.flashcard_pool:
            return
        self.current_word_index = (self.current_word_index + 1) % len(self.flashcard_pool)
        self.show_current_flashcard()

    # --- ЛОГИКА ВИКТОРИНЫ ---
    def start_quiz(self):
        if len(self.words_data) < 4:
            messagebox.showwarning("Внимание", "Для викторины нужно минимум 4 слова в базе!")
            return
        self.hide_all_frames()
        self.quiz_frame.pack(expand=True, fill="both")
        self.quiz_words = random.sample(self.words_data, len(self.words_data))
        self.current_word_index = 0
        self.quiz_correct_answers = 0
        self.next_quiz_question()

    def next_quiz_question(self):
        if self.current_word_index >= len(self.quiz_words) or self.current_word_index >= 10:
            messagebox.showinfo("Викторина окончена",
                                f"Ваш результат: {self.quiz_correct_answers} из {min(10, len(self.quiz_words))}")
            self.show_main_menu()
            return

        for btn in self.quiz_buttons:
            btn.configure(fg_color="#444444", hover_color="#555555", state="normal")

        correct_word = self.quiz_words[self.current_word_index]
        self.quiz_word_label.configure(text=f"Как переводится:\n\n{correct_word['word']}?")
        self.correct_answer_text = correct_word['translation']

        wrong_options = [w['translation'] for w in self.words_data if w['translation'] != self.correct_answer_text]
        options = random.sample(wrong_options, min(3, len(wrong_options))) + [self.correct_answer_text]
        random.shuffle(options)

        for i, btn in enumerate(self.quiz_buttons):
            if i < len(options):
                btn.configure(text=options[i])
                btn.pack(pady=8, fill="x", padx=40)
            else:
                btn.pack_forget()

    def check_quiz_answer(self, btn_index):
        selected_text = self.quiz_buttons[btn_index].cget("text")
        if selected_text == self.correct_answer_text:
            self.quiz_buttons[btn_index].configure(fg_color="green", hover_color="green")
            self.quiz_correct_answers += 1
        else:
            self.quiz_buttons[btn_index].configure(fg_color=self.color_red, hover_color=self.color_red)
            for btn in self.quiz_buttons:
                if btn.cget("text") == self.correct_answer_text:
                    btn.configure(fg_color="green", hover_color="green")

        for btn in self.quiz_buttons:
            btn.configure(state="disabled")
        self.root.after(1500, self.advance_quiz)

    def advance_quiz(self):
        self.current_word_index += 1
        self.next_quiz_question()

    # --- ЛОГИКА ИГРЫ С ПРЕДЛОЖЕНИЯМИ ---
    def start_sentence_game(self):
        self.hide_all_frames()
        self.sentence_frame.pack(expand=True, fill="both")
        self._clear_sentence_widgets()

        if not self.sentences_data:
            self.sentence_target_label.configure(text="Нет предложений для игры.")
            return

        self.current_sentence = random.choice(self.sentences_data)
        self.sentence_target_label.configure(
            text=f"Рус: {self.current_sentence['russian']}\nСоберите нем. предложение:")

        self.sentence_words = self.current_sentence['words'].copy()
        random.shuffle(self.sentence_words)

        for word in self.sentence_words:
            lbl = ctk.CTkButton(self.sentence_container, text=word, font=ctk.CTkFont(family="Ebbe", size=18),
                                width=120, height=50, fg_color="#666666", hover_color="#888888",
                                command=lambda w=word: self._add_word_to_sentence(w))
            lbl.pack(side="left", padx=10, pady=10)

    def _add_word_to_sentence(self, word):
        lbl = ctk.CTkLabel(self.sentence_container, text=word,
                           font=ctk.CTkFont(family="Ebbe", size=18, weight="bold"), fg_color="#333333",
                           text_color="white", width=120, height=50)
        lbl.bind("<Button-1>", lambda e, w=word: self._return_word_to_pool(w, lbl))
        lbl.pack(side="left", padx=10, pady=10)
        self.sentence_labels.append((lbl, word))

        if word in self.sentence_words:
            self.sentence_words.remove(word)

        for widget in self.sentence_container.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == word:
                widget.destroy()
                break

    def _return_word_to_pool(self, word, label_widget):
        label_widget.destroy()
        self.sentence_labels = [(l, w) for l, w in self.sentence_labels if w != word]
        self.sentence_words.append(word)

        btn = ctk.CTkButton(self.sentence_container, text=word, font=ctk.CTkFont(family="Ebbe", size=18),
                            width=120, height=50, fg_color="#666666", hover_color="#888888",
                            command=lambda w=word: self._add_word_to_sentence(w))
        btn.pack(side="left", padx=10, pady=10)

    def _undo_last_word(self):
        if not self.sentence_labels:
            return

        last_label, last_word = self.sentence_labels.pop()
        last_label.destroy()

        self.sentence_words.append(last_word)

        btn = ctk.CTkButton(self.sentence_container, text=last_word, font=ctk.CTkFont(family="Ebbe", size=18),
                            width=120, height=50, fg_color="#666666", hover_color="#888888",
                            command=lambda w=last_word: self._add_word_to_sentence(w))
        btn.pack(side="left", padx=10, pady=10)

    def _clear_sentence_widgets(self):
        for widget in self.sentence_container.winfo_children():
            widget.destroy()
        for lbl, _ in self.sentence_labels:
            lbl.destroy()
        self.sentence_labels.clear()

    def check_sentence(self):
        user_answer = ' '.join([word for _, word in self.sentence_labels])
        correct_answer = ' '.join(self.current_sentence['words'])

        if user_answer == correct_answer:
            messagebox.showinfo("Успех", "Предложение составлено верно!")
        else:
            messagebox.showwarning("Ошибка", f"Правильно:\n{correct_answer}")

        self._clear_sentence_widgets()

    # --- СПРАВОЧНИК И СЛОВАРЬ ---
    def show_grammar(self):
        self.hide_all_frames()
        self.grammar_frame.pack(expand=True, fill="both")

    def show_dictionary(self):
        self.hide_all_frames()
        self.dict_frame.pack(expand=True, fill="both")
        self.dict_textbox.configure(state="normal", font=ctk.CTkFont(family="Ebbe", size=16))
        self.dict_textbox.delete("1.0", "end")
        if not self.words_data:
            self.dict_textbox.insert("1.0", "Словарь пуст.")
        else:
            for item in sorted(self.words_data, key=lambda x: x['word']):
                article = item.get('article', '') + ' ' if item.get('article') else ''
                self.dict_textbox.insert("end", f"{article}{item['word']} — {item['translation']}\n")
        self.dict_textbox.configure(state="disabled")


if __name__ == "__main__":
    root = ctk.CTk()
    app = DeutschTrainerApp(root)
    root.mainloop()

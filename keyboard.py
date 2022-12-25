from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class CreateKeyboard:
    def __init__(self):
        self.btn_search = ['Поиск', VkKeyboardColor.SECONDARY]
        self.btn_view = ['Просмотреть избранное', VkKeyboardColor.PRIMARY]
        self.btn_finish = ['Закончить', VkKeyboardColor.SECONDARY]
        self.btn_next = ['Дальше', VkKeyboardColor.PRIMARY]
        self.btn_favorite = ['В избранное', VkKeyboardColor.POSITIVE]
        self.btn_black = ['В ЧС', VkKeyboardColor.NEGATIVE]
        self.btn_bro = ['Пока, бро!', VkKeyboardColor.SECONDARY]
        self.btn_hi = ['Привет', VkKeyboardColor.POSITIVE]

    def _create_button(self, buttons):
        '''Создаем кнопку'''
        keyboard = VkKeyboard(one_time=True)
        for button in buttons:
            if button[2] == 'True':
                keyboard.add_line()
            keyboard.add_button(button[0], color=button[1])
        return keyboard.get_keyboard()

    def hi(self):
        return self._create_button([self.btn_search + ['False'],
                                    self.btn_view + ['True'],
                                    self.btn_finish + ['True']])

    def search(self):
        return self._create_button([self.btn_next + ['False'],
                                    self.btn_favorite + ['True'],
                                    self.btn_view + ['False'],
                                    self.btn_black + ['True'],
                                    self.btn_finish + ['True']])

    def view(self):
        return self._create_button([self.btn_next + ['False'],
                                    self.btn_finish + ['True']])

    def favorite(self):
        return self._create_button([self.btn_next + ['False'],
                                    self.btn_view + ['True'],
                                    self.btn_finish + ['True']])

    def finish(self):
        return self._create_button([self.btn_bro + ['False'],
                                    self.btn_next + ['True']])

    def bro(self):
        return self._create_button([self.btn_hi + ['False']])

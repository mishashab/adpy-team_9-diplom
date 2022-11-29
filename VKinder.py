from pprint import pprint


class VKinder:

    def __init__(self, longpoll, session):
        self.longpoll = longpoll
        self.session = session

    def _search(self, user_param):
        '''Грязный первоначальный поис'''
        result = self.session.users.search(count=5, blacklisted_by_me=0, fields=['photo_id', 'sex', 'bdate', 'city'],
                                           city=user_param['city_id'], sex=user_param['gender'],
                                           age_from=user_param['age'], age_to=user_param['age'], has_photo=1,
                                           is_closed=False, can_access_closed=True)['items']
        return result

    def _find_photo(self, user_id):
        '''Подбираем фото'''
        get_photo = self.session.photos.get(owner_id=user_id, album_id='profile', extended=1, photo_sizes=1)['items']
        photo_list = sorted(get_photo, key=lambda k: k['likes']['count'], reverse=True)
        if len(photo_list) > 3:
            photo_list = photo_list[:3]
        attachment_list = list()
        for item in photo_list:
            attachment_list.append(f'photo{user_id}_{item["id"]}')
        attachment = ','.join(attachment_list)
        return attachment

    def find_user(self, user_param):
        '''выборка по параметрам'''
        search_users_dict = self._search(user_param)
        find_users = list()
        for fined_user in search_users_dict:
            attachment = self._find_photo(fined_user['id'])
            find_users.append({'name': f"{fined_user['first_name']} "
                                       f"{fined_user['last_name']}",
                               'url': f"https://vk.com/id{fined_user['id']}",
                               'attachment': attachment})

        # pprint(find_users)
        return find_users

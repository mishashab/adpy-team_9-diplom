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
        res = self.session.photos.get(owner_id=user_id, album_id='profile')
        return res

    def find_user(self, user_param):
        '''выборка по параметрам'''
        search_users_dict = self._search(user_param)
        find_users = list()
        photo = self._find_photo(search_users_dict[1]['id'])
        find_users.append({'name': f"{search_users_dict[1]['first_name']} "
                                   f"{search_users_dict[1]['last_name']}",
                           'url': f"https://vk.com/id{search_users_dict[1]['id']}"})
        # pprint(search_users_dict)
        pprint(photo)
        return find_users

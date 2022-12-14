from django.test import TestCase
from rest_framework.test import APITestCase
from .models import User, UserImage, Ticket, Turn
from django.contrib.auth.models import Group, Permission
from rest_framework_simplejwt.tokens import RefreshToken
import datetime


class UrlTest(APITestCase):

    def setUp(self):
        admin_permissions = Permission.objects.filter(codename__in=[
            'view_user', 'add_user', 'change_user', 'delete_user',
            'view_userimage', 'add_userimage', 'change_userimage', 'delete_userimage',
            'view_notification', 'add_notification', 'change_notification', 'delete_notification',
            'view_notificationtype', 'add_notificationtype', 'change_notificationtype', 'delete_notificationtype',
            'view_turn', 'add_turn', 'change_turn', 'delete_turn',
            'view_ticket', 'add_ticket', 'change_ticket', 'delete_ticket',
        ])
        employee_permissions = Permission.objects.filter(
            codename__in=['view_ticket', 'add_ticket', 'change_ticket', 'delete_ticket'])
        end_permissions = Permission.objects.filter(
            codename__in=['view_userimage', 'add_userimage', 'change_userimage', 'delete_userimage', 'view_ticket', 'add_ticket', 'change_ticket', 'delete_ticket'])
        g_admin = Group.objects.create(name='admin_user')
        g_employee = Group.objects.create(name='employee_user')
        g_coworker = Group.objects.create(name='coworker_user')
        g_end = Group.objects.create(name='end_user')
        g_admin.permissions.set(admin_permissions)
        g_employee.permissions.set(employee_permissions)
        g_end.permissions.set(end_permissions)
        self.u_admin = User.objects.create(
            username='u_admin', password='mmmmm46456456456')
        self.u_admin.groups.add(Group.objects.get(name='admin_user'))
        self.u_employee = User.objects.create(
            username='u_employee', password='mmmmm46456456456', admin=self.u_admin)
        self.u_employee.groups.add(Group.objects.get(name='employee_user'))
        self.u_coworker = User.objects.create(
            username='u_coworker', password='mmmmm46456456456', admin=self.u_admin)
        self.u_coworker.groups.set([Group.objects.get(name='employee_user')])
        self.u_end = User.objects.create(
            username='u_end', password='mmmmm46456456456', admin=self.u_admin)
        self.u_end.groups.add(Group.objects.get(name='end_user'))

    def __jwt_auth(self, user):
        refresh_token = RefreshToken().for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + str(refresh_token.access_token))
        self.expected_status_users = 200 if user.has_perm(
            'users.view_user') else 403
        self.expected_status_users_add = 200 if user.has_perm(
            'users.add_user') else 403
        self.expected_status_users_change = 200 if user.has_perm(
            'users.change_user') else 403

    def test_users_url(self):
        for user in [self.u_admin, self.u_employee, self.u_end]:
            self.__jwt_auth(user)
            r_users = self.client.get('/api/users/users/', format='json')
            self.assertEqual(r_users.status_code,
                             self.expected_status_users)

    def test_can_create_users(self):
        for user in [self.u_admin, self.u_employee, self.u_end]:
            self.__jwt_auth(user)
            create_user_data = {
                'username': 'test_'+user.username,
                'first_name': 'test',
                'last_name': 'testian',
                'email': 'test@test.test',
                'gender': 'Male',
            }
            r_users_add = self.client.post(
                '/api/users/users/', data=create_user_data, format='json')
            self.assertEqual(r_users_add.status_code,
                             self.expected_status_users_add)

    def test_can_change_own_sub_users(self):
        for user in [self.u_admin, self.u_employee]:
            self.__jwt_auth(user)
            if user == self.u_employee:
                sub_user = user.admin.subUsers.all()[0]
            else:
                sub_user = user.subUsers.all()[0]
            r_users_change = self.client.patch(
                '/api/users/users/'+str(sub_user.id)+'/', data={'username': 'test2', 'fist_name': 'test2', 'last_name': 'testian2'}, format='json')
            self.assertEqual(r_users_change.status_code,
                             self.expected_status_users_change)

    def test_cant_change_other_sub_users(self):
        other_admin = User.objects.create(
            username='u_other_admin', password='mmmmm46456456456')

        other_admin.groups.add(Group.objects.get(name='admin_user'))
        sub_user = User.objects.create(
            username='u_other_admin_sub', password='mmmmm46456456456')
        other_admin.subUsers.set([sub_user])
        self.__jwt_auth(self.u_admin)
        r_users_change = self.client.patch(
            '/api/users/users/'+str(sub_user.id)+'/', data={'username': 'test2', 'fist_name': 'test2', 'last_name': 'testian2'}, format='json')
        self.assertEqual(r_users_change.status_code,
                         403)

    def test_can_edit_profile(self):
        for user in [self.u_admin, self.u_employee, self.u_end]:
            self.__jwt_auth(user)

            r_edit_profile = self.client.patch(
                '/api/users/EditProfile', data={'username': 'test2', 'fist_name': 'test22', 'last_name': 'testian2'}, format='json')
            self.assertEqual(r_edit_profile.status_code, 200)

    def test_can_add_and_remove_image_for_own_sub_user(self):
        self.__jwt_auth(self.u_admin)
        sub_user = self.u_end
        image = open('files/images/aicon.png', 'rb')
        r_user_image_add = self.client.post(
            '/api/users/usersImage/', data={'image': image, 'user': sub_user.id})
        self.assertEqual(r_user_image_add.status_code, 200)
        # print(r_user_image_add.data)
        r_user_image_remove = self.client.delete(
            '/api/users/usersImage/'+str(r_user_image_add.data['created_image']['id'])+'/')
        self.assertEqual(r_user_image_remove.status_code, 200)

    def test_cant_add_and_remove_image_for_own_sub_user(self):
        other_admin = User.objects.create(
            username='u_other_admin', password='mmmmm46456456456')
        # create another admin user
        other_admin.groups.add(Group.objects.get(name='admin_user'))
        # consider first global u_end(sub user of first admin) as sub user
        sub_user = self.u_end
        # authenticate with new admin which created in this test
        self.__jwt_auth(other_admin)

        # test other admin can not add image for su user of u_admin
        with open('files/images/aicon.png', 'rb') as image:
            r_user_image_add = self.client.post(
                '/api/users/usersImage/', data={'image': image, 'user': sub_user.id})
        self.assertEqual(r_user_image_add.status_code, 403)

        # authenticate with u_admin
        self.__jwt_auth(self.u_admin)

        # add image for u_end
        with open('files/images/aicon.png', 'rb') as image:
            r_user_image_add = self.client.post(
                '/api/users/usersImage/', data={'image': image, 'user': sub_user.id})

        # test other admin can not remove u_end image
        self.__jwt_auth(other_admin)
        r_user_image_remove = self.client.delete(
            '/api/users/usersImage/'+str(r_user_image_add.data['created_image']['id'])+'/')
        self.assertEqual(r_user_image_remove.status_code, 403)

        # remove created image
        self.__jwt_auth(self.u_admin)
        self.client.delete(
            '/api/users/usersImage/'+str(r_user_image_add.data['created_image']['id'])+'/')

    def test_can_add_ticket(self):
        self.__jwt_auth(self.u_end)
        r_add_tickets = self.client.post('/api/users/tickets/', data={'message_type': 'Management',
                                                                      'status': 'Waiting',
                                                                      'subject': 'test',
                                                                      'user': self.u_end.id,
                                                                      'text': 'hello world!',
                                                                      }, format='json')
        self.assertEqual(r_add_tickets.status_code, 201)

    def test_can_see_own_tickets(self):
        for user in [self.u_admin, self.u_employee, self.u_end]:
            self.__jwt_auth(user)
            r_tickets = self.client.get('/api/users/tickets/', format='json')
            self.assertEqual(r_tickets.status_code, 200)

    def test_can_see_one_ticket_of_own(self):
        other_user = User.objects.create(
            username='u_other_user', password='mmmmm46456456456')
        for user in [self.u_admin, self.u_employee, self.u_end]:
            self.__jwt_auth(user)
            own_ticket = Ticket.objects.create(
                subject='own_ticket', user=user, text='its my own', message_type='Support', status='Waiting')
            r_ticket_own = self.client.get(
                '/api/users/tickets/'+str(own_ticket.id)+'/', format='json')
            self.assertEqual(r_ticket_own.status_code, 200)
            # create another admin user
            other_user.groups.add(Group.objects.get(name='end_user'))
            other_user_ticket = Ticket.objects.create(
                subject='own_ticket', user=other_user, text='its my own', message_type='Support', status='Waiting')
            r_ticket_other = self.client.get(
                '/api/users/tickets/'+str(other_user_ticket.id)+'/', format='json')
            self.assertEqual(r_ticket_other.status_code, 404)

    def test_can_create_employee(self):
        expected_statuses = [201, 403, 403]
        for idx, user in enumerate([self.u_admin, self.u_employee, self.u_end]):
            self.__jwt_auth(user)
            create_user_data = {
                'username': 'test_'+user.username,
                'first_name': 'test',
                'last_name': 'testian',
                'email': 'test@test.test',
                'gender': 'Male',
            }
            r_employee_add = self.client.post(
                '/api/users/employees/', data=create_user_data, format='json')
            self.assertEqual(r_employee_add.status_code,
                             expected_statuses[idx])

    def test_can_change_own_sub_users(self):
        expected_statuses = [200, 403, 403]
        for idx, user in enumerate([self.u_admin, self.u_employee]):
            self.__jwt_auth(user)
            sub_user = User.objects.create(username='test_'+str(idx), first_name='test',
                                           last_name='test', admin=user)
            r_users_change = self.client.patch(
                '/api/users/employees/'+str(sub_user.id)+'/', data={'username': 'test2', 'fist_name': 'test2', 'last_name': 'testian2'}, format='json')
            self.assertEqual(r_users_change.status_code,
                             expected_statuses[idx])

    def test_cant_change_other_sub_users(self):
        other_admin = User.objects.create(
            username='u_other_admin', password='mmmmm46456456456')

        other_admin.groups.add(Group.objects.get(name='admin_user'))
        sub_user = User.objects.create(
            username='u_other_admin_sub', password='mmmmm46456456456')
        other_admin.subUsers.set([sub_user])
        self.__jwt_auth(self.u_admin)
        r_users_change = self.client.patch(
            '/api/users/employees/'+str(sub_user.id)+'/', data={'username': 'test2', 'fist_name': 'test2', 'last_name': 'testian2'}, format='json')
        self.assertEqual(r_users_change.status_code,
                         403)

    def test_can_see_permission(self):
        expected_statuses = [200, 403, 403]
        for idx, user in enumerate([self.u_admin, self.u_employee, self.u_end]):
            self.__jwt_auth(user)
            sub_user = User.objects.create(
                username='u_sub'+str(idx), password='mmmmm46456456456', admin=user)
            r_permission_list = self.client.get(
                '/api/users/UserPermissionList/'+str(sub_user.id), format='json')
            self.assertEqual(r_permission_list.status_code,
                             expected_statuses[idx])

    def test_can_change_permission(self):
        expected_statuses = [204, 403, 403]
        for idx, user in enumerate([self.u_admin, self.u_employee, self.u_end]):
            self.__jwt_auth(user)
            sub_user = User.objects.create(
                username='u_sub'+str(idx), password='mmmmm46456456456', admin=user)
            r_permission_change = self.client.patch(
                '/api/users/ChangeUserPermissionList/'+str(sub_user.id), data={'permission_id': [61, 62, 63, 64]}, format='json')
            self.assertEqual(r_permission_change.status_code,
                             expected_statuses[idx])

    def test_admin_can_read_turns(self):
        self.__jwt_auth(self.u_admin)
        r_turns_list = self.client.get(
            '/api/users/readTurns/', format='json')
        self.assertEqual(r_turns_list.status_code, 200)

    def test_employee_can_read_turns(self):
        self.__jwt_auth(self.u_employee)
        permissions = Permission.objects.filter(codename__in=[
            'view_turn', 'add_turn', 'change_turn', 'delete_turn',
        ])
        self.u_employee.user_permissions.set(permissions)
        r_turns_list = self.client.get(
            '/api/users/readTurns/', format='json')
        self.assertEqual(r_turns_list.status_code, 200)

    def test_employee_cant_read_turns(self):
        self.__jwt_auth(self.u_employee)
        r_turns_list = self.client.get(
            '/api/users/readTurns/', format='json')
        self.assertEqual(r_turns_list.status_code, 403)

    def test_admin_can_read_single_turn(self):
        self.__jwt_auth(self.u_admin)
        turn = Turn.objects.create(
            date_visit=datetime.datetime.now().replace(tzinfo=datetime.timezone.utc), description='test', user=self.u_end)
        r_turns_list = self.client.get(
            '/api/users/readTurns/'+str(turn.id)+'/', format='json')
        self.assertEqual(r_turns_list.status_code, 200)

    def test_employee_can_read_single_turn(self):
        self.__jwt_auth(self.u_employee)
        turn = Turn.objects.create(
            date_visit=datetime.datetime.now().replace(tzinfo=datetime.timezone.utc), description='test', user=self.u_end)
        permissions = Permission.objects.filter(codename__in=[
            'view_turn', 'add_turn', 'change_turn', 'delete_turn',
        ])
        self.u_employee.user_permissions.set(permissions)
        r_turns_list = self.client.get(
            '/api/users/readTurns/'+str(turn.id)+'/', format='json')
        self.assertEqual(r_turns_list.status_code, 200)

    def test_employee_cant_read_single_turn(self):
        self.__jwt_auth(self.u_employee)
        turn = Turn.objects.create(
            date_visit=datetime.datetime.now().replace(tzinfo=datetime.timezone.utc), description='test', user=self.u_end)
        r_turns_list = self.client.get(
            '/api/users/readTurns/'+str(turn.id)+'/', format='json')
        self.assertEqual(r_turns_list.status_code, 403)

    def test_admin_can_add_turn(self):
        self.__jwt_auth(self.u_admin)

        r_turns_add = self.client.post(
            '/api/users/turns/', data={'date_visit': '1401-01-20 14:25', 'user': self.u_end.id}, format='json')
        self.assertEqual(r_turns_add.status_code, 201)

    def test_employee_can_add_turn(self):
        self.__jwt_auth(self.u_employee)
        permissions = Permission.objects.filter(codename__in=[
            'view_turn', 'add_turn', 'change_turn', 'delete_turn',
        ])
        self.u_employee.user_permissions.set(permissions)
        r_turns_add = self.client.post(
            '/api/users/turns/', data={'date_visit': '1401-01-20 14:25', 'user': self.u_end.id}, format='json')
        self.assertEqual(r_turns_add.status_code, 201)

    def test_employee_cant_add_turn(self):
        self.__jwt_auth(self.u_employee)
        r_turns_add = self.client.post(
            '/api/users/turns/', data={'date_visit': '1401-01-20 14:25', 'user': self.u_end.id}, format='json')
        self.assertEqual(r_turns_add.status_code, 403)

    def test_admin_can_change_turn(self):
        self.__jwt_auth(self.u_admin)
        turn = Turn.objects.create(
            date_visit=datetime.datetime.now().replace(tzinfo=datetime.timezone.utc), description='test', user=self.u_end)
        r_turns_change = self.client.patch(
            '/api/users/turns/'+str(turn.id)+'/', data={'date_visit': '1401-01-20 14:25', 'user': self.u_end.id}, format='json')
        self.assertEqual(r_turns_change.status_code, 200)

    def test_employee_can_change_turn(self):
        self.__jwt_auth(self.u_employee)
        turn = Turn.objects.create(
            date_visit=datetime.datetime.now().replace(tzinfo=datetime.timezone.utc), description='test', user=self.u_end)
        permissions = Permission.objects.filter(codename__in=[
            'view_turn', 'add_turn', 'change_turn', 'delete_turn',
        ])
        self.u_employee.user_permissions.set(permissions)
        r_turns_change = self.client.patch(
            '/api/users/turns/'+str(turn.id)+'/', data={'date_visit': '1401-01-20 15:25'}, format='json')
        self.assertEqual(r_turns_change.status_code, 200)

    def test_employee_cant_change_turn(self):
        self.__jwt_auth(self.u_employee)
        turn = Turn.objects.create(
            date_visit=datetime.datetime.now().replace(tzinfo=datetime.timezone.utc), description='test', user=self.u_end)
        r_turns_change = self.client.patch(
            '/api/users/turns/'+str(turn.id)+'/', data={'date_visit': '1401-01-20 15:25'}, format='json')
        self.assertEqual(r_turns_change.status_code, 403)

    def test_admin_can_remove_turn(self):
        self.__jwt_auth(self.u_admin)
        turn = Turn.objects.create(
            date_visit=datetime.datetime.now().replace(tzinfo=datetime.timezone.utc), description='test', user=self.u_end)
        r_turns_remove = self.client.delete(
            '/api/users/turns/'+str(turn.id)+'/', format='json')
        self.assertEqual(r_turns_remove.status_code, 204)

    def test_employee_can_remove_turn(self):
        self.__jwt_auth(self.u_employee)
        turn = Turn.objects.create(
            date_visit=datetime.datetime.now().replace(tzinfo=datetime.timezone.utc), description='test', user=self.u_end)
        permissions = Permission.objects.filter(codename__in=[
            'view_turn', 'add_turn', 'change_turn', 'delete_turn',
        ])
        self.u_employee.user_permissions.set(permissions)
        r_turns_remove = self.client.delete(
            '/api/users/turns/'+str(turn.id)+'/', format='json')
        self.assertEqual(r_turns_remove.status_code, 204)

    def test_employee_cant_remove_turn(self):
        self.__jwt_auth(self.u_employee)
        turn = Turn.objects.create(
            date_visit=datetime.datetime.now().replace(tzinfo=datetime.timezone.utc), description='test', user=self.u_end)
        r_turns_remove = self.client.delete(
            '/api/users/turns/'+str(turn.id)+'/', format='json')
        self.assertEqual(r_turns_remove.status_code, 403)

    def test_admin_can_read_coworkers(self):
        self.__jwt_auth(self.u_admin)
        r_coworkers_read = self.client.get(
            '/api/users/coworkers/', format='json')
        self.assertEqual(r_coworkers_read.status_code, 200)

    def test_admin_can_create_coworkers(self):
        self.__jwt_auth(self.u_admin)
        r_coworkers_read = self.client.post(
            '/api/users/coworkers/', data={
                'username': 'test_coworker',
                'commission': 18,
                'first_name': 'test',
                'last_name': 'coworker',
                'email': 'test@test.test',
                'gender': 'Female',
            }, format='json')
        self.assertEqual(r_coworkers_read.status_code, 201)

    def test_admin_can_update_coworkers(self):
        self.__jwt_auth(self.u_admin)
        user = User.objects.create(
            username='test_coworker2', commission=25, gender='Female', admin=self.u_admin)
        user.groups.set([Group.objects.get(name='coworker_user')])
        r_coworkers_read = self.client.patch(
            '/api/users/coworkers/'+str(user.id)+"/", data={
                'username': 'test_coworker',
                'commission': 18,
                'first_name': 'test',
                'last_name': 'coworker',
                'email': 'test@test.test',
                'gender': 'Male',
            }, format='json')
        self.assertEqual(r_coworkers_read.status_code, 200)

    # def test_

from validation.param_check import ParamCheck


class MembersCardParamCheck(ParamCheck):
    def __init__(self, params):
        self.mode = params['mode'] if 'mode' in params else None

        self.error_msg = []

    def check_api_members_card(self):
        self.check_mode()

        return self.error_msg

    def check_mode(self):
        if error := self.check_required(self.mode, 'mode'):
            self.error_msg.append(error)
            return

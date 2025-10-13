class SlackUtils:
    def NO_OP(self, *args):
        """
        No operation.
        """
        pass

    def action_with_params(self, action, params=[]):
        """
        Max length of return is 255 characters.
        Slack will return a 200 but not display UI
        if action_id is greater than this limit.
        """
        if not isinstance(action, str):
            raise TypeError("action must be str")
        if not isinstance(params, list):
            raise TypeError("params must be list")
        output = action + "?" + "&".join(params)
        if len(output) > 255:
            raise ValueError("action_id would be longer than 255 characters")
        return output

    def process_action_id(self, action_string):
        output = {}
        x = action_string.split("?")
        output["true_id"] = x[0]
        output["params"] = {}
        if len(x) > 1:
            ps_list = x[1].split("&")
            for param_str in ps_list:
                b = param_str.split("=")
                output["params"][b[0]] = b[1]
        return output

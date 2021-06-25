class EnvironmentSelectionError(Exception):
    pass

class EnvironmentSessions:

    def __init__(self, lm=None, arm=None):
        self.__lm = lm
        self.__arm = arm
        self.__lm_updated = False
        self.__arm_updated = False
        self.__brent_updated = False

    @property
    def lm(self):
        if not self.__lm:
            raise EnvironmentSelectionError('No CP4NA orchestration environment provided')
        return self.__lm

    @property
    def arm(self):
        if not self.__arm:
            raise EnvironmentSelectionError('No AnsibleRM environment was provided')
        return self.__arm

    def mark_lm_updated(self):
        self.__lm_updated = True

    def is_lm_updated(self):
        if self.__lm:
            return self.__lm_updated
        return False

    def mark_arm_updated(self):
        self.__arm_updated = True

    def is_arm_updated(self):
        if self.__arm:
            return self.__arm_updated
        return False

    def mark_brent_updated(self):
        self.__brent_updated = True

    def is_brent_updated(self):
        if self.__lm:
            return self.__brent_updated
        return False
from custom_python_logger.logger import get_logger

class InstanceManager:
    def __init__(self):
        self.logger = get_logger(__class__.__name__)
        self._instances = []

    def add(self, instance):
        self._instances.append(instance)

    def close_all(self):
        for instance in reversed(self._instances):
            _instance_name = instance.__class__.__name__
            try:
                if hasattr(instance, 'close'):
                    instance.close()
                else:  # hasattr(instance, '__exit__'):
                    instance.__exit__(None, None, None)
                self.logger.info(f"Instance: {_instance_name} closed successfully.")
            except Exception as e:
                self.logger.info(f"Failed to close instance {instance}: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_all()


def main():
    class SomeInstance:
        def __init__(self, add_to_instance_manager: bool = False):
            self.logger = get_logger(__class__.__name__)

            if add_to_instance_manager:
                instance_manager.add(self)

        @property
        def __class_name__(self):
            return self.__class__.__name__

        def __enter__(self):
            self.logger.info(f"Entering {self.__class_name__}")
            return self

        def __exit__(self, exc_type, exc_value, exc_traceback):
            self.logger.info(f"Exiting {self.__class_name__}")
            # Handle any cleanup here
            if exc_type:
                self.logger.info(f"Exception: {exc_value}")
            return True

    SomeInstance(add_to_instance_manager=True)

    resource1 = open('file1.txt', 'w')
    resource2 = open('file2.txt', 'w')

    instance_manager.add(resource1)
    instance_manager.add(resource2)

    # do stuff...

    instance_manager.close_all()  # or, if inside `with manager:`, it will happen automatically


if __name__ == "__main__":
    instance_manager = InstanceManager()

    main()

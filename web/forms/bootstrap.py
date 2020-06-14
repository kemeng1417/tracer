class BootStrapForm(object):
    """ 写一个类,以便后面的模板继承 """

    bootstrap_class_exclude = []
    # 重写父类方法，加上class
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if name in self.bootstrap_class_exclude:
                continue
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入{}'.format(field.label)
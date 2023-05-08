from django.forms import ModelForm
from .models import Room
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import Submit
from django.urls import reverse
from crispy_forms.bootstrap import InlineField

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['name','private','allow_anon']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.form_class = 'd-flex form-inline bg-light mb-3 px-3 gap-4 justify-content-center flex-nowrap'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('room_settings', kwargs={'room_id': self.instance.room_id})
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            InlineField('name'),
            InlineField('private'),
        )

class CreateRoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.form_class = 'd-flex form-inline bg-light mb-3 px-3 gap-4 justify-content-center flex-nowrap'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('create_room')
        self.helper.add_input(Submit('create', 'Submit'))
        self.helper.layout = Layout(
            InlineField('name'),
        )
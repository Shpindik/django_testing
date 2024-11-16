from http import HTTPStatus

from django.core.management import call_command
from django.utils.text import slugify

from notes.forms import WARNING
from notes.models import Note

from .base import BaseTestCase


class TestNoteEditDelete(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.initial_title = self.note.title
        self.initial_text = self.note.text
        self.initial_slug = self.note.slug
        self.initial_author = self.note.author

    def test_create_note_authorized(self):
        Note.objects.all().delete()
        response = self.auth_client.post(
            self.add_url, data=self.form_data
        )
        self.assertRedirects(response, self.success_url)
        note = Note.objects.get(title=self.TITLE)
        self.assertEqual(note.title, self.TITLE)
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])

    def test_create_note_unauthorized(self):
        Note.objects.all().delete()
        self.client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_create_note_duplicate_slug(self):
        response = self.auth_client.post(self.add_url, data=self.FORM_DATA_1)
        self.assertFormError(response, 'form', 'slug', WARNING)
        self.assertEqual(Note.objects.count(), 0)

    def test_create_note_auto_slug(self):
        call_command('flush', '--no-input')
        response = self.auth_client.post(self.add_url, data=self.FORM_DATA_2)
        self.assertRedirects(response, self.success_url)
        generated_slug = slugify(self.FORM_DATA_2['title'])
        self.assertTrue(Note.objects.filter(slug=generated_slug).exists())

    def test_author_can_edit(self):
        response = self.auth_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.auth_client.user)

    def test_author_can_delete(self):
        initial_notes_count = Note.objects.count()
        response = self.auth_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        final_notes_count = Note.objects.count()
        self.assertEqual(final_notes_count, initial_notes_count - 1)

    def note_not_updated(self):
        self.note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(self.note.title, self.initial_title)
        self.assertEqual(self.note.text, self.initial_text)
        self.assertEqual(self.note.slug, self.initial_slug)
        self.assertEqual(self.note.author, self.initial_author)

    def test_another_user_cannot_edit(self):
        response = self.another_client.post(
            self.edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note_not_updated()

    def test_another_user_cannot_delete(self):
        initial_notes_count = Note.objects.count()
        response = self.another_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note_not_updated()
        self.assertEqual(Note.objects.count(), initial_notes_count)

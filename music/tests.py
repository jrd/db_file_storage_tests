# python imports
import mimetypes
import os
from urllib import urlencode

# django imports
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

# project imports
from .models import CD, CDDisc, CDCover


CDS_DATA = {
    'btw': {
        'name': 'By The Way',
        'cover_path': os.path.join(settings.TEST_FILES_DIR, 'btw_cover.jpg'),
        'disc1_path': os.path.join(settings.TEST_FILES_DIR, 'btw_disc1.png'),
        'disc2_path': os.path.join(settings.TEST_FILES_DIR, 'btw_disc2.jpg'),
    },
    'gh': {
        'name': 'Greatest Hits',
        'cover_path': os.path.join(settings.TEST_FILES_DIR, 'gh_cover.jpg'),
        'disc1_path': os.path.join(settings.TEST_FILES_DIR, 'gh_disc1.jpg'),
        'disc2_path': os.path.join(settings.TEST_FILES_DIR, 'gh_disc2.jpg'),
    },
}


def get_cd(cd_key):
    assert cd_key in CDS_DATA
    name = CDS_DATA[cd_key]['name']
    return CD.objects.get(name=name)


class AddEditAndDeleteCDsTests(TestCase):
    def __init__(self, *args, **kwargs):
        super(AddEditAndDeleteCDsTests, self).__init__(*args, **kwargs)
        self.cover_count = 0
        self.disc_count = 0

    def assert_pictures_count(self):
        self.assertEqual(CDCover.objects.count(), self.cover_count)
        self.assertEqual(CDDisc.objects.count(), self.disc_count)

    def add_or_edit_cd(
        self, method, cd_key, with_cover_pic, with_disc_pic,
        disc_pic_nbr=None, clear_cover=False, clear_disc=False
    ):
        """
            Create or edit a CD.
        """
        assert method in ('add', 'edit')
        assert cd_key in CDS_DATA
        if with_disc_pic:
            assert disc_pic_nbr in (1, 2)

        if method == 'add':
            url = reverse('cd.add')
        else:  # edit
            cd = get_cd(cd_key=cd_key)
            url = reverse('cd.edit', kwargs={'pk': cd.pk})

        cd_data = CDS_DATA[cd_key]
        form_data = {'name': cd_data['name']}

        cover_file = None
        disc_file = None

        if with_cover_pic:
            cover_file = open(cd_data['cover_path'], 'rb')
            form_data['cover'] = cover_file
        elif clear_cover:
            form_data['cover-clear'] = 'on'

        if with_disc_pic:
            disc_file = open(cd_data['disc%s_path' % disc_pic_nbr], 'rb')
            form_data['disc'] = disc_file
        elif clear_disc:
            form_data['disc-clear'] = 'on'

        response = self.client.post(url, form_data, follow=True)

        if cover_file:
            cover_file.close()
        if disc_file:
            disc_file.close()
        return response

    def assert_pic_is_correct(self, cd_key, pic, disc_pic_nbr=None):
        """
            Assert that the CD has the correct picture.
        """
        assert cd_key in CDS_DATA
        assert pic in ('cover', 'disc')
        if pic == 'disc':
            assert disc_pic_nbr in (1, 2)

        cd = get_cd(cd_key=cd_key)
        cd_data = CDS_DATA[cd_key]

        if pic == 'cover':
            picture_path = cd_data['cover_path']
        else:  # disc
            picture_path = cd_data['disc%s_path' % disc_pic_nbr]

        download_url = reverse('db_file_storage.download_file')
        if pic == 'cover':
            download_url += '?' + urlencode({'name': cd.cover.name})
        else:  # disc
            download_url += '?' + urlencode({'name': cd.disc.name})

        response = self.client.get(download_url)

        with open(picture_path, 'rb') as pic_file:
            # Assert that the contents of the saved picture are correct
            self.assertEqual(pic_file.read(), response.content)

        # Assert that the mimetype of the saved picture is correct
        self.assertEqual(
            mimetypes.guess_type(picture_path)[0],
            response['Content-Type']
        )

    def test(self):
        # Add "By The Way" (BTW) CD without disc and cover pictures.
        self.add_or_edit_cd(
            method='add',
            cd_key='btw',
            with_cover_pic=False,
            with_disc_pic=False
        )
        self.assert_pictures_count()

        # Assert BTW's pictures fields are empty
        cd = get_cd(cd_key='btw')
        self.assertEqual(cd.disc.name, '')
        self.assertEqual(cd.cover.name, '')

        # Edit BTW CD: add disc picture
        self.add_or_edit_cd(
            method='edit',
            cd_key='btw',
            with_cover_pic=False,
            with_disc_pic=True,
            disc_pic_nbr=1
        )
        self.disc_count += 1
        self.assert_pictures_count()

        # Assert that the contents of the new BTW disc picture are correct
        self.assert_pic_is_correct(cd_key='btw', pic='disc', disc_pic_nbr=1)

        # Assert BTW's cover picture field is still empty
        cd = get_cd(cd_key='btw')
        self.assertEqual(cd.cover.name, '')

        # Edit BTW CD: add cover picture
        self.add_or_edit_cd(
            method='edit',
            cd_key='btw',
            with_cover_pic=True,
            with_disc_pic=False
        )
        self.cover_count += 1
        self.assert_pictures_count()

        # Assert that the contents of the BTW disc picture are still correct
        self.assert_pic_is_correct(cd_key='btw', pic='disc', disc_pic_nbr=1)

        # Assert that the contents of the new BTW cover picture are correct
        self.assert_pic_is_correct(cd_key='btw', pic='cover')

        # Edit BTW CD: change disc picture
        self.add_or_edit_cd(
            method='edit',
            cd_key='btw',
            with_cover_pic=False,
            with_disc_pic=True,
            disc_pic_nbr=2
        )
        self.assert_pictures_count()

        # Assert that the contents of the new BTW disc picture are correct
        self.assert_pic_is_correct(cd_key='btw', pic='disc', disc_pic_nbr=2)

        # Assert that the contents of the BTW cover picture are still correct
        self.assert_pic_is_correct(cd_key='btw', pic='cover')

        # Edit BTW CD: clear cover picture
        self.add_or_edit_cd(
            method='edit',
            cd_key='btw',
            with_cover_pic=False,
            with_disc_pic=False,
            clear_cover=True
        )
        self.cover_count -= 1
        self.assert_pictures_count()

        # Assert BTW's cover picture field is empty now
        cd = get_cd(cd_key='btw')
        self.assertEqual(cd.cover.name, '')

        # Assert that the contents of the BTW disc picture are still correct
        self.assert_pic_is_correct(cd_key='btw', pic='disc', disc_pic_nbr=2)

        # Add "Greatest hits" (GH) CD with disc and cover pictures.
        self.add_or_edit_cd(
            method='add',
            cd_key='gh',
            with_cover_pic=True,
            with_disc_pic=True,
            disc_pic_nbr=1
        )
        self.cover_count += 1
        self.disc_count += 1
        self.assert_pictures_count()

        """
            From now on, after each change in any of the CDs,
              we check if the pictures are correct for both of them,
              to ensure that saving/deleting pictures of a CD doesn't
              interfere with the pictures of the other one.
        """

        # Assert BTW's cover picture field is still empty
        cd = get_cd(cd_key='btw')
        self.assertEqual(cd.cover.name, '')

        # Assert that the contents of the BTW disc picture are still correct
        self.assert_pic_is_correct(cd_key='btw', pic='disc', disc_pic_nbr=2)

        # Assert that the contents of the GH cover picture are correct
        self.assert_pic_is_correct(cd_key='gh', pic='cover')

        # Assert that the contents of the GH disc picture are correct
        self.assert_pic_is_correct(cd_key='gh', pic='disc', disc_pic_nbr=1)

        # Edit GH CD: clear disc picture
        self.add_or_edit_cd(
            method='edit',
            cd_key='gh',
            with_cover_pic=False,
            with_disc_pic=False,
            clear_disc=True
        )
        self.disc_count -= 1
        self.assert_pictures_count()

        # Assert BTW's cover picture field is still empty
        cd = get_cd(cd_key='btw')
        self.assertEqual(cd.cover.name, '')

        # Assert that the contents of the BTW disc picture are still correct
        self.assert_pic_is_correct(cd_key='btw', pic='disc', disc_pic_nbr=2)

        # Assert that the contents of the GH cover picture are still correct
        self.assert_pic_is_correct(cd_key='gh', pic='cover')

        # Assert GH's disc picture field is empty now
        cd = get_cd(cd_key='gh')
        self.assertEqual(cd.disc.name, '')

        # Edit BTW CD: add cover picture
        self.add_or_edit_cd(
            method='edit',
            cd_key='btw',
            with_cover_pic=True,
            with_disc_pic=False
        )
        self.cover_count += 1
        self.assert_pictures_count()

        # Assert that the contents of the BTW cover picture are correct
        self.assert_pic_is_correct(cd_key='btw', pic='cover')

        # Assert that the contents of the BTW disc picture are still correct
        self.assert_pic_is_correct(cd_key='btw', pic='disc', disc_pic_nbr=2)

        # Assert that the contents of the GH cover picture are still correct
        self.assert_pic_is_correct(cd_key='gh', pic='cover')

        # Assert GH's disc picture field is still empty
        cd = get_cd(cd_key='gh')
        self.assertEqual(cd.disc.name, '')

        # Edit GH CD: add disc picture
        self.add_or_edit_cd(
            method='edit',
            cd_key='gh',
            with_cover_pic=False,
            with_disc_pic=True,
            disc_pic_nbr=2
        )
        self.disc_count += 1
        self.assert_pictures_count()

        # Assert that the contents of the BTW cover picture are still correct
        self.assert_pic_is_correct(cd_key='btw', pic='cover')

        # Assert that the contents of the BTW disc picture are still correct
        self.assert_pic_is_correct(cd_key='btw', pic='disc', disc_pic_nbr=2)

        # Assert that the contents of the GH cover picture are still correct
        self.assert_pic_is_correct(cd_key='gh', pic='cover')

        # Assert that the contents of the GH disc picture are correct
        self.assert_pic_is_correct(cd_key='gh', pic='disc', disc_pic_nbr=2)

        # Deleting BTW CD
        cd = get_cd(cd_key='btw')
        cd.delete()
        self.cover_count -= 1
        self.disc_count -= 1
        self.assert_pictures_count()

        # Assert that the contents of the GH cover picture are still correct
        self.assert_pic_is_correct(cd_key='gh', pic='cover')

        # Assert that the contents of the GH disc picture are still correct
        self.assert_pic_is_correct(cd_key='gh', pic='disc', disc_pic_nbr=2)

        # Deleting GH CD
        cd = get_cd(cd_key='gh')
        cd.delete()
        self.cover_count -= 1
        self.disc_count -= 1
        self.assertEqual(self.cover_count, 0)
        self.assertEqual(self.disc_count, 0)
        self.assert_pictures_count()
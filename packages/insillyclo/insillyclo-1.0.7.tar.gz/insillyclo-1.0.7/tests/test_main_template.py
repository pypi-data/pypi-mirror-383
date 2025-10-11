#
#  InSillyClo
#  Copyright (C) 2025  The InSillyClo Authors
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import pathlib
from tempfile import NamedTemporaryFile

from click.testing import CliRunner

import insillyclo.additional_exception
import insillyclo.main
import insillyclo.models
import insillyclo.observer
import insillyclo.parser
from tests.base_test_case import BaseTestCase


class TestTemplate(BaseTestCase):
    maxDiff = None

    def test_count(self):
        with NamedTemporaryFile() as file:
            runner = CliRunner()
            result = runner.invoke(
                insillyclo.main.cli,
                [
                    '--debug',
                    '--fail-on-error',
                    'template',
                    file.name,
                    '--nb-input-parts',
                    4,
                    '--separator',
                    '-',
                    '-e',
                    'BbsI',
                    '--name',
                    'foobar',
                ],
            )
            self.assertInvokeWorks(result)

            assembly, plasmids = self.load_filled_templates(file.name, load_only_assembly=True)
            self.assertEqual(0, len(plasmids))
            self.assertEqual(
                ["InputPart1", "InputPart2", "InputPart3", "InputPart4"],
                [ip.name for ip in assembly.input_parts],
            )
            self.assertEqual("BbsI", assembly.enzyme)
            self.assertEqual("foobar", assembly.name)

    def test_name(self):
        with NamedTemporaryFile() as file:
            runner = CliRunner()
            result = runner.invoke(
                insillyclo.main.cli,
                [
                    '--debug',
                    '--fail-on-error',
                    'template',
                    file.name,
                    '--input-part',
                    'riri',
                    '--input-part',
                    'fifi',
                    '-p',
                    'loulou',
                    '--separator',
                    '-',
                    '--restriction-enzyme-goldengate',
                    'BsaI',
                ],
            )
            self.assertInvokeWorks(result)

            assembly, plasmids = self.load_filled_templates(file.name, load_only_assembly=True)
            self.assertEqual(0, len(plasmids))
            self.assertEqual(
                ["riri", "fifi", "loulou"],
                [ip.name for ip in assembly.input_parts],
            )

    def test_short(self):
        with NamedTemporaryFile() as file:
            runner = CliRunner()
            result = runner.invoke(
                insillyclo.main.cli,
                [
                    '--debug',
                    '--fail-on-error',
                    'template',
                    file.name,
                    '-p',
                    'riri',
                    '--input-part',
                    'fifi',
                    '-p',
                    'loulou',
                    '-s',
                    '-',
                    '--restriction-enzyme-goldengate',
                    'BsaI',
                    '-n',
                    'My Assembly',
                ],
            )
            self.assertInvokeWorks(result)

            assembly, plasmids = self.load_filled_templates(file.name, load_only_assembly=True)
            self.assertEqual(0, len(plasmids))
            self.assertEqual(
                ["riri", "fifi", "loulou"],
                [ip.name for ip in assembly.input_parts],
            )
            self.assertEqual('My Assembly', assembly.name)
            self.assertEqual('-', assembly.separator)
            self.assertEqual('BsaI', assembly.enzyme)

    def test_count_or_names_not_both(self):
        self.assertRaises(
            ValueError,
            insillyclo.main.cli,
            [
                '--debug',
                '--fail-on-error',
                'template',
                '/tmp/foo.bar',
                '--nb-input-parts',
                4,
                '--input-part',
                'riri',
                '--input-part',
                'fifi',
                '--separator',
                '-',
                '-e',
                'BbsI',
                '--name',
                'foobar',
            ],
        )

    def test_template_generated_with_no_param(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            template = pathlib.Path('template.xlsx')
            print(template.absolute())
            self.assertFalse(template.exists())
            result = runner.invoke(
                insillyclo.main.cli,
                [
                    'template',
                ],
            )
            self.assertInvokeWorks(result)
            self.assertTrue(template.exists())

            self.assertRaises(
                insillyclo.additional_exception.EnzymeNotFound,
                insillyclo.parser.parse_assembly_and_plasmid_from_template,
                input_template_filled=template.absolute(),
                input_part_factory=insillyclo.models.InputPartDataClassFactory(),
                assembly_factory=insillyclo.models.AssemblyDataClassFactory(),
                plasmid_factory=insillyclo.models.PlasmidDataClassFactory(),
                observer=self.get_cli_observer(debug=False, fail_on_error=False),
                load_only_assembly=True,
            )

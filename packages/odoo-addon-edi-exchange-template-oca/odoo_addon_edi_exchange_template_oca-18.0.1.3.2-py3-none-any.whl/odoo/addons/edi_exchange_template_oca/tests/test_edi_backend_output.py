# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import datetime
import json

from freezegun import freeze_time
from lxml import etree
from odoo_test_helper import FakeModelLoader

from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase


class TestEDIBackendOutputBase(EDIBackendCommonTestCase):
    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    @classmethod
    def _setup_records(cls):
        res = super()._setup_records()
        # Load fake models ->/
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from odoo.addons.edi_core_oca.tests.fake_models import EdiTestExecution

        cls.loader.update_registry((EdiTestExecution,))
        cls.ExecutionAbstractModel = cls.env["edi.framework.test.execution"]
        cls.model = cls.env["ir.model"].search(
            [("model", "=", "edi.framework.test.execution")]
        )
        cls.exchange_type_out.generate_model_id = cls.env.ref(
            "edi_exchange_template_oca.model_edi_oca_template_handler"
        )
        cls.exchange_type_out.send_model_id = cls.model
        cls.exchange_type_out.output_validate_model_id = cls.model
        cls.exchange_type_out.check_model_id = cls.model
        # We do that in order to ensure that the tests work properly with edi_connector
        cls.type_out1 = cls._create_exchange_type(
            name="Template output 1",
            direction="output",
            code="test_type_out1",
            exchange_file_ext="txt",
            generate_model_id=cls.env.ref(
                "edi_exchange_template_oca.model_edi_oca_template_handler"
            ).id,
            send_model_id=cls.model.id,
            output_validate_model_id=cls.model.id,
            check_model_id=cls.model.id,
            exchange_filename_pattern="{record.ref}-{type.code}-{dt}",
        )
        model = cls.env["edi.exchange.template.output"]
        qweb_tmpl = cls.env["ir.ui.view"].create(
            {
                "type": "qweb",
                "key": "edi_exchange.test_output1",
                "arch": """
            <t t-name="edi_exchange.test_output1">
                <t t-esc="record.ref" /> - <t t-esc="record.name" />
            </t>
            """,
            }
        )
        cls.tmpl_out1 = model.create(
            {
                "code": "edi.output.generate.demo_backend.test_type_out1",
                "name": "Out 1",
                "backend_type_id": cls.backend.backend_type_id.id,
                "generator": "qweb",
                "template_id": qweb_tmpl.id,
                "output_type": "txt",
            }
        )
        cls.type_out1.output_template_id = cls.tmpl_out1
        cls.tmpl_out1.allowed_type_ids = cls.type_out1
        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
        }
        cls.record1 = cls.backend.create_record("test_type_out1", vals)

        cls.type_out2 = cls._create_exchange_type(
            name="Template output 2",
            direction="output",
            code="test_type_out2",
            exchange_file_ext="xml",
            generate_model_id=cls.env.ref(
                "edi_exchange_template_oca.model_edi_oca_template_handler"
            ).id,
            send_model_id=cls.model.id,
            output_validate_model_id=cls.model.id,
            check_model_id=cls.model.id,
            exchange_filename_pattern="{record.ref}-{type.code}-{dt}",
        )
        qweb_tmpl = cls.env["ir.ui.view"].create(
            {
                "type": "qweb",
                "key": "edi_exchange.test_output2",
                "arch": """
            <t t-name="edi_exchange.test_output2">
                <t t-name="edi_exchange.test_output2">
                    <Record t-att-ref="record.ref">
                        <Name t-esc="record.name" />
                        <Custom t-att-bit="custom_bit" t-esc="baz"/>
                    </Record>
                </t>
            </t>
            """,
            }
        )
        cls.tmpl_out2 = model.create(
            {
                "code": "edi.output.generate.demo_backend.test_type_out2",
                "name": "Out 2",
                "backend_type_id": cls.backend.backend_type_id.id,
                "generator": "qweb",
                "template_id": qweb_tmpl.id,
                "output_type": "xml",
                "code_snippet": """
foo = "custom_var"
baz = 2
result = {"custom_bit": foo, "baz": baz}
                """,
            }
        )
        cls.type_out2.output_template_id = cls.tmpl_out2
        cls.tmpl_out2.allowed_type_ids = cls.type_out2
        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
            "type_id": cls.type_out2.id,
        }
        cls.record2 = cls.backend.create_record("test_type_out2", vals)
        cls.type_out3 = cls._create_exchange_type(
            name="Template output 3",
            direction="output",
            code="test_type_out3",
            exchange_file_ext="xml",
            generate_model_id=cls.env.ref(
                "edi_exchange_template_oca.model_edi_oca_template_handler"
            ).id,
            send_model_id=cls.model.id,
            output_validate_model_id=cls.model.id,
            check_model_id=cls.model.id,
            exchange_filename_pattern="{record.id}-{type.code}-{dt}",
        )
        cls.report = cls.env.ref("web.action_report_externalpreview")
        cls.tmpl_out3 = model.create(
            {
                "code": "edi.output.generate.demo_backend.test_type_out3",
                "name": "Out 3",
                "backend_type_id": cls.backend.backend_type_id.id,
                "generator": "report",
                "report_id": cls.report.id,
                "output_type": "pdf",
                "code_snippet": """
result = {"res_ids": record.ids}
                        """,
            }
        )
        cls.type_out3.output_template_id = cls.tmpl_out3
        cls.tmpl_out3.allowed_type_ids = cls.type_out3
        company = cls.env.ref("base.main_company")
        vals = {
            "model": company._name,
            "res_id": company.id,
            "type_id": cls.type_out2.id,
        }
        cls.record3 = cls.backend.create_record("test_type_out3", vals)

        cls.type_out_json = cls._create_exchange_type(
            name="Template output JSON",
            direction="output",
            code="test_type_out_json",
            generate_model_id=cls.env.ref(
                "edi_exchange_template_oca.model_edi_oca_template_handler"
            ).id,
            send_model_id=cls.model.id,
            output_validate_model_id=cls.model.id,
            check_model_id=cls.model.id,
            exchange_file_ext="txt",
            exchange_filename_pattern="{record.ref}-{type.code}-{dt}",
        )
        model = cls.env["edi.exchange.template.output"]
        cls.tmpl_out_json = model.create(
            {
                "generator": "json",
                "name": "Out JSON",
                "backend_type_id": cls.backend.backend_type_id.id,
                "code": "test_type_out_json",
                "output_type": "json",
                "code_snippet": """
result = {
    'payload': {
            "name": record.name,
            "ref": record.ref
    }
}
                """,
            }
        )
        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
            "type_id": cls.tmpl_out_json.id,
        }
        cls.record_json = cls.backend.create_record("test_type_out_json", vals)
        return res


# TODO: add more unit tests
class TestEDIBackendOutput(TestEDIBackendOutputBase):
    def test_get_template(self):
        self.assertEqual(
            self.backend._get_output_template(self.record1), self.tmpl_out1
        )
        self.assertEqual(
            self.backend._get_output_template(self.record2), self.tmpl_out2
        )
        self.assertEqual(
            self.backend._get_output_template(self.record_json), self.tmpl_out_json
        )

    def test_generate_file(self):
        self.backend.exchange_generate(self.record1)
        expected = f"{self.partner.ref} - {self.partner.name}"
        file_content = self.record1._get_file_content()
        self.assertEqual(file_content.strip(), expected)
        self.backend.exchange_generate(self.record2)
        file_content = self.record2._get_file_content()
        doc = etree.fromstring(file_content)
        self.assertEqual(doc.tag, "Record")
        self.assertEqual(doc.attrib, {"ref": self.partner.ref})
        self.assertEqual(doc.getchildren()[0].tag, "Name")
        self.assertEqual(doc.getchildren()[0].text, self.partner.name)
        self.assertEqual(doc.getchildren()[1].tag, "Custom")
        self.assertEqual(doc.getchildren()[1].text, "2")
        self.assertEqual(doc.getchildren()[1].attrib, {"bit": "custom_var"})
        self.backend.exchange_generate(self.record_json)
        expected = json.dumps({"name": self.partner.name, "ref": self.partner.ref})
        file_content = self.record_json._get_file_content()
        self.assertEqual(file_content.strip(), expected)

    def test_prettify(self):
        self.tmpl_out2.template_id.arch = (
            '<t t-name="edi_exchange.test_output2"><root><a>1</a></root></t>'
        )
        output = self.tmpl_out2.exchange_generate(self.record2)
        self.assertEqual(output, b"<root><a>1</a></root>")
        self.tmpl_out2.prettify = True
        output = self.tmpl_out2.exchange_generate(self.record2)
        self.assertEqual(output, b"<root>\n  <a>1</a>\n</root>\n")

    def test_generate_file_report(self):
        self.backend.exchange_generate(self.record3)
        file_content = self.record3._get_file_content()
        self.assertEqual(
            self.report._render(self.report, [self.record3.res_id])[0]
            .strip()
            .decode("UTF-8"),
            file_content.strip(),
        )

    def test_date_to_string(self):
        dt = datetime.date(2024, 9, 10)
        no_dt = ""
        converted_dt_utc = self.tmpl_out1._date_to_string(dt)
        converted_dt_non_utc = self.tmpl_out1._date_to_string(dt, False)
        converted_no_dt = self.tmpl_out1._date_to_string(no_dt)
        self.assertEqual(converted_dt_utc, "2024-09-10")
        self.assertEqual(converted_dt_non_utc, "2024-09-10")
        self.assertEqual(converted_no_dt, "")

    def test_datetime_to_string(self):
        dt = datetime.datetime(2024, 9, 10, 11, 5, 49)
        no_dt = ""
        converted_dt_utc = self.tmpl_out1._datetime_to_string(dt)
        converted_dt_non_utc = self.tmpl_out1._datetime_to_string(dt, False)
        converted_no_dt = self.tmpl_out1._datetime_to_string(no_dt)
        self.assertEqual(converted_dt_utc, "2024-09-10 00:00:00")
        self.assertEqual(converted_dt_non_utc, "2024-09-10 11:05:49")
        self.assertEqual(converted_no_dt, "")

    @freeze_time("2024-07-27 10:00:00")
    def test_utc_now(self):
        utc_now_output = self.tmpl_out1._utc_now()
        self.assertEqual(utc_now_output, "2024-07-27T10:00:00")

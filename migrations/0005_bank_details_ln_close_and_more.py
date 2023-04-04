# Generated by Django 4.1.2 on 2023-02-04 09:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tools_management', '0020_rename_with_gst_toolspurchase_invoice_without_gst'),
        ('accounts', '0004_bank_details_account_type_bank_details_ln_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bank_details',
            name='ln_close',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='purchase_paymentdetails',
            name='general_le',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='p_details', to='accounts.general_ledger'),
        ),
        migrations.AlterField(
            model_name='purchaseinvref',
            name='refinvno',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='purchase_payment', to='tools_management.toolspurchase_invoice'),
        ),
    ]

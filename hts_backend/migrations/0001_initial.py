# Generated by Django 2.0.4 on 2018-04-25 20:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='accessed_user',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_time', models.DateTimeField(auto_created=True, auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Activity_Log',
            fields=[
                ('log_time', models.DateTimeField(auto_created=True, null=True)),
                ('log_idx', models.AutoField(primary_key=True, serialize=False)),
                ('uname', models.CharField(default='a', max_length=200)),
                ('User_Activity', models.CharField(max_length=200)),
                ('Market_Activity', models.CharField(max_length=200)),
                ('System_Activity', models.CharField(max_length=200)),
                ('Admin_Activity', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': '회원, 시스템, 관리자 활동로그',
            },
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Estimated_Profit', models.BigIntegerField(default=0)),
                ('Realized_Profit', models.BigIntegerField(default=0)),
                ('Total_Profit', models.BigIntegerField(default=0)),
                ('losscut_left', models.BigIntegerField(default=0)),
                ('poured_money', models.BigIntegerField(default=0)),
                ('Actual_money_by_now', models.BigIntegerField(default=0)),
                ('lended_loan_by_now', models.BigIntegerField(default=0)),
                ('used_money', models.BigIntegerField(default=0)),
                ('available_money', models.BigIntegerField(default=0)),
                ('Dam_bo_geum', models.BigIntegerField(default=0)),
            ],
            options={
                'verbose_name': '회원 자산',
            },
        ),
        migrations.CreateModel(
            name='Deposit_Withdraw_Order_Done_List',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TransDateTime', models.DateTimeField(auto_created=True, auto_now=True, null=True)),
                ('Order_Money_Plus_Minus', models.IntegerField(default=2)),
                ('Order', models.IntegerField(default=2)),
                ('MoneyBefore', models.IntegerField(default=0)),
                ('PlusMinus', models.IntegerField(default=0)),
                ('MoneyNow', models.IntegerField(default=0)),
                ('WhoDidThisTransaction', models.CharField(default='', max_length=100)),
            ],
            options={
                'verbose_name': '총 입/출금 요청과 처리 내역',
            },
        ),
        migrations.CreateModel(
            name='Entire_Shares',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Share_Category', models.IntegerField()),
                ('Share_Code', models.CharField(max_length=100)),
                ('Share_Name', models.CharField(max_length=100)),
                ('Is_feasible', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': '전체 종목 리스트',
            },
        ),
        migrations.CreateModel(
            name='Holdings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Share_Name', models.CharField(default='a', max_length=100, null=True)),
                ('Holding_Quantities', models.IntegerField(default=0)),
                ('Price_Per_Single', models.FloatField(default=0)),
                ('Total_Bought_Prices', models.IntegerField(default=0)),
                ('Total_Current_Prices', models.IntegerField(default=0)),
                ('Estimated_Profit_In_This_Stock', models.IntegerField(default=0)),
                ('OverNight_Quant', models.IntegerField(default=0)),
                ('OverNight_Rest_Days', models.IntegerField(default=30)),
                ('Should_OvN_be_released', models.BooleanField(default=False)),
                ('Share_idx', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.Entire_Shares')),
            ],
            options={
                'verbose_name': '회원별 잔고 목록',
            },
        ),
        migrations.CreateModel(
            name='List_Not_Done',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Order_Type', models.IntegerField(default=0)),
                ('Order_Price', models.IntegerField(default=0)),
                ('Order_Quant', models.IntegerField(default=0)),
                ('Share_Name', models.CharField(default='a', max_length=100, null=True)),
                ('Is_Cancelled', models.BooleanField(default=False)),
                ('Share_idx', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.Entire_Shares')),
            ],
            options={
                'verbose_name': '미체결 매수/매도 주문 내역',
            },
        ),
        migrations.CreateModel(
            name='Loan_Order_Done',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Order_Date', models.DateTimeField(auto_created=True, auto_now=True)),
                ('Stock_Loan_Rate', models.IntegerField(default=0)),
                ('Dam_bo_geum', models.IntegerField(default=0)),
                ('Is_Done', models.BooleanField(default=False)),
                ('Done_Date', models.DateTimeField(default=None, null=True)),
            ],
            options={
                'verbose_name': '대출 요청과 처리 내역',
            },
        ),
        migrations.CreateModel(
            name='MarketStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_Time', models.TimeField(auto_created=True, auto_now=True)),
                ('current_DayTime', models.DateTimeField(auto_created=True, auto_now=True)),
                ('update_time_setter', models.IntegerField()),
                ('is_market_opened', models.BooleanField(default=False)),
                ('is_market_exceptionally_closed', models.BooleanField(default=False)),
                ('LossCutRate', models.FloatField(default=0.15)),
                ('BasicFeeBuy', models.FloatField(default=0.01)),
                ('BasicFeeSell', models.FloatField(default=0.01)),
                ('SellFee', models.FloatField(default=0.02)),
                ('BuyFee', models.FloatField(default=0.02)),
            ],
            options={
                'verbose_name': '시장상태',
            },
        ),
        migrations.CreateModel(
            name='Profit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Date_jeong_san', models.DateField(auto_created=True, auto_now=True)),
                ('Total_Estimated_Profit_From_Stocks', models.BigIntegerField(default=0)),
                ('Total_Realized_Profit_Except_Fees', models.BigIntegerField(default=0)),
                ('TOTAL_PROFIT_BY_NOW', models.BigIntegerField(default=0)),
                ('Real_Profit_Today', models.BigIntegerField(default=0)),
            ],
            options={
                'verbose_name': '회원별 일별 수익',
            },
        ),
        migrations.CreateModel(
            name='RD_Related_To_Shares',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Share_Code', models.CharField(default='a', max_length=50)),
                ('RDDictString', models.TextField(default='')),
                ('Supplied_by', models.IntegerField(default=-1)),
                ('Is_Called_Second', models.BooleanField(default=False)),
                ('Is_BasicSet', models.BooleanField(default=False)),
                ('Share_idx', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.Entire_Shares')),
            ],
            options={
                'verbose_name': '조회중인 종목 정보 큐',
            },
        ),
        migrations.CreateModel(
            name='Share_Groups_Per_User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interest_group', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': '관심 그룹 목록',
            },
        ),
        migrations.CreateModel(
            name='Share_Interest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Share_Category', models.IntegerField()),
                ('Share_Code', models.CharField(max_length=100)),
                ('Share_Name', models.CharField(max_length=100)),
                ('Share_idx', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.Entire_Shares')),
                ('interest_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.Share_Groups_Per_User')),
            ],
            options={
                'verbose_name': '회원별 관심 그룹, 관심 종목',
            },
        ),
        migrations.CreateModel(
            name='SignInReq',
            fields=[
                ('user_idx', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.CharField(max_length=50, unique=True)),
                ('user_pw', models.CharField(max_length=500)),
                ('bank_id', models.CharField(max_length=100)),
                ('user_pn', models.CharField(max_length=100, null=True)),
                ('user_bank_name', models.CharField(max_length=50)),
                ('user_name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': '회원가입 요청',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TransDateTime', models.DateTimeField(auto_created=True, auto_now=True, null=True)),
                ('Order_Type', models.IntegerField(default=-1)),
                ('TreatStatus', models.IntegerField(default=-1)),
                ('Order_Quant', models.IntegerField(default=0)),
                ('Order_Price', models.IntegerField(default=0)),
                ('Trans_Quant', models.IntegerField(default=0)),
                ('Trans_Price', models.IntegerField(default=0)),
                ('Fee_In_Trans', models.IntegerField(default=0)),
                ('Selling_Profit', models.IntegerField(default=0)),
                ('Realized_Profit', models.IntegerField(default=0)),
                ('Deposit_Money', models.IntegerField(default=0)),
                ('OtherMsg', models.CharField(default=' ', max_length=100)),
                ('Actual_money', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.Asset')),
                ('Share_idx', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.Entire_Shares')),
            ],
            options={
                'verbose_name': '총 거래 내역: 입/출금, 매수/매도 주문 요청과 처리 내역',
            },
        ),
        migrations.CreateModel(
            name='User_In',
            fields=[
                ('user_idx', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.CharField(max_length=50, unique=True)),
                ('user_pw', models.CharField(max_length=500)),
                ('bank_id', models.CharField(max_length=100)),
                ('user_pn', models.CharField(max_length=100, null=True)),
                ('user_bank_name', models.CharField(max_length=50)),
                ('user_name', models.CharField(max_length=50)),
                ('total_access_time', models.IntegerField(blank=True, null=True)),
                ('shut_down', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': '회원목록',
            },
        ),
        migrations.AddField(
            model_name='transaction',
            name='user_idx',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.User_In'),
        ),
        migrations.AddField(
            model_name='share_interest',
            name='user_idx',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.User_In'),
        ),
        migrations.AddField(
            model_name='share_groups_per_user',
            name='user_idx',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.User_In'),
        ),
        migrations.AddField(
            model_name='profit',
            name='user_idx',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.User_In'),
        ),
        migrations.AddField(
            model_name='loan_order_done',
            name='user_idx',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.User_In'),
        ),
        migrations.AddField(
            model_name='list_not_done',
            name='Transaction_idx',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.Transaction'),
        ),
        migrations.AddField(
            model_name='list_not_done',
            name='user_idx',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.User_In'),
        ),
        migrations.AddField(
            model_name='holdings',
            name='user_idx',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.User_In'),
        ),
        migrations.AlterUniqueTogether(
            name='entire_shares',
            unique_together={('Share_Category', 'Share_Code')},
        ),
        migrations.AddField(
            model_name='deposit_withdraw_order_done_list',
            name='Transaction_idx',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.Transaction'),
        ),
        migrations.AddField(
            model_name='deposit_withdraw_order_done_list',
            name='user_idx',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.User_In'),
        ),
        migrations.AddField(
            model_name='asset',
            name='user_idx',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.User_In'),
        ),
        migrations.AddField(
            model_name='activity_log',
            name='user_idx',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.User_In'),
        ),
        migrations.AddField(
            model_name='accessed_user',
            name='user_asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.Asset'),
        ),
        migrations.AddField(
            model_name='accessed_user',
            name='user_idx',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.User_In'),
        ),
        migrations.AlterUniqueTogether(
            name='share_interest',
            unique_together={('user_idx', 'interest_group', 'Share_idx')},
        ),
        migrations.AlterUniqueTogether(
            name='share_groups_per_user',
            unique_together={('user_idx', 'interest_group')},
        ),
    ]

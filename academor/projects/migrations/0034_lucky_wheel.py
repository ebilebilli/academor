from django.db import migrations, models
import django.db.models.deletion


DEFAULT_PRIZES = [
    {
        'label_line1_az': '10%',
        'label_line1_en': '10%',
        'label_line1_ru': '10%',
        'label_line2_az': 'endirim',
        'label_line2_en': 'off',
        'label_line2_ru': 'скидка',
        'title_az': '10% endirim qazandın',
        'title_en': 'You won 10% off',
        'title_ru': 'Вы выиграли скидку 10%',
        'code': 'LUCKY10',
        'weight': 20,
        'is_win': True,
        'is_respin': False,
        'order': 10,
    },
    {
        'label_line1_az': 'Pulsuz',
        'label_line1_en': 'Free',
        'label_line1_ru': 'Бесплатная',
        'label_line2_az': 'çatdırılma',
        'label_line2_en': 'delivery',
        'label_line2_ru': 'доставка',
        'title_az': 'Pulsuz çatdırılma qazandın',
        'title_en': 'You won free delivery',
        'title_ru': 'Вы выиграли бесплатную доставку',
        'code': 'FREESHIP',
        'weight': 18,
        'is_win': True,
        'is_respin': False,
        'order': 20,
    },
    {
        'label_line1_az': '5%',
        'label_line1_en': '5%',
        'label_line1_ru': '5%',
        'label_line2_az': 'endirim',
        'label_line2_en': 'off',
        'label_line2_ru': 'скидка',
        'title_az': '5% endirim qazandın',
        'title_en': 'You won 5% off',
        'title_ru': 'Вы выиграли скидку 5%',
        'code': 'LUCKY5',
        'weight': 24,
        'is_win': True,
        'is_respin': False,
        'order': 30,
    },
    {
        'label_line1_az': 'Növbəti',
        'label_line1_en': 'Try',
        'label_line1_ru': 'В',
        'label_line2_az': 'dəfə',
        'label_line2_en': 'again',
        'label_line2_ru': 'другой раз',
        'title_az': 'Bu dəfə olmadı',
        'title_en': 'Not this time',
        'title_ru': 'В этот раз не повезло',
        'code': '',
        'weight': 12,
        'is_win': False,
        'is_respin': False,
        'order': 40,
    },
    {
        'label_line1_az': '15%',
        'label_line1_en': '15%',
        'label_line1_ru': '15%',
        'label_line2_az': 'endirim',
        'label_line2_en': 'off',
        'label_line2_ru': 'скидка',
        'title_az': '15% endirim qazandın',
        'title_en': 'You won 15% off',
        'title_ru': 'Вы выиграли скидку 15%',
        'code': 'LUCKY15',
        'weight': 10,
        'is_win': True,
        'is_respin': False,
        'order': 50,
    },
    {
        'label_line1_az': 'Sürpriz',
        'label_line1_en': 'Surprise',
        'label_line1_ru': 'Сюрприз',
        'label_line2_az': 'hədiyyə',
        'label_line2_en': 'gift',
        'label_line2_ru': 'подарок',
        'title_az': 'Sürpriz hədiyyə qazandın',
        'title_en': 'You won a surprise gift',
        'title_ru': 'Вы выиграли сюрприз-подарок',
        'code': 'GIFT2026',
        'weight': 6,
        'is_win': True,
        'is_respin': False,
        'order': 60,
    },
    {
        'label_line1_az': '20%',
        'label_line1_en': '20%',
        'label_line1_ru': '20%',
        'label_line2_az': 'endirim',
        'label_line2_en': 'off',
        'label_line2_ru': 'скидка',
        'title_az': '20% endirim qazandın',
        'title_en': 'You won 20% off',
        'title_ru': 'Вы выиграли скидку 20%',
        'code': 'LUCKY20',
        'weight': 3,
        'is_win': True,
        'is_respin': False,
        'order': 70,
    },
    {
        'label_line1_az': 'Yenidən',
        'label_line1_en': 'Spin',
        'label_line1_ru': 'Крутить',
        'label_line2_az': 'fırlat',
        'label_line2_en': 'again',
        'label_line2_ru': 'ещё раз',
        'title_az': 'Bir cəhd də sənindir',
        'title_en': 'You get another try',
        'title_ru': 'Вам даётся ещё одна попытка',
        'code': '',
        'weight': 7,
        'is_win': False,
        'is_respin': True,
        'order': 80,
    },
]


def seed_prizes(apps, schema_editor):
    Prize = apps.get_model('projects', 'LuckyWheelPrize')
    if Prize.objects.exists():
        return
    Prize.objects.bulk_create([Prize(**row) for row in DEFAULT_PRIZES])


def unseed_prizes(apps, schema_editor):
    Prize = apps.get_model('projects', 'LuckyWheelPrize')
    Prize.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0033_media_test_take_poster_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='LuckyWheelPrize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label_line1_az', models.CharField(max_length=40, verbose_name='Label line 1 (AZ)')),
                ('label_line1_en', models.CharField(blank=True, max_length=40, verbose_name='Label line 1 (EN)')),
                ('label_line1_ru', models.CharField(blank=True, max_length=40, verbose_name='Label line 1 (RU)')),
                ('label_line2_az', models.CharField(blank=True, max_length=40, verbose_name='Label line 2 (AZ)')),
                ('label_line2_en', models.CharField(blank=True, max_length=40, verbose_name='Label line 2 (EN)')),
                ('label_line2_ru', models.CharField(blank=True, max_length=40, verbose_name='Label line 2 (RU)')),
                ('title_az', models.CharField(help_text='Shown in the result dialog, e.g. “You won 10% off”.', max_length=200, verbose_name='Result title (AZ)')),
                ('title_en', models.CharField(blank=True, max_length=200, verbose_name='Result title (EN)')),
                ('title_ru', models.CharField(blank=True, max_length=200, verbose_name='Result title (RU)')),
                ('code', models.CharField(blank=True, help_text='Optional coupon code shown when the user wins.', max_length=64, verbose_name='Coupon code')),
                ('weight', models.PositiveIntegerField(default=10, help_text='Higher weight = more likely to land on this prize.', verbose_name='Weight')),
                ('is_win', models.BooleanField(default=True, help_text='If enabled, this outcome is treated as a win (confetti, coupon).', verbose_name='Winning prize')),
                ('is_respin', models.BooleanField(default=False, help_text='If enabled, the user may spin again after this result.', verbose_name='Allow another spin')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='Active')),
                ('order', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Order')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Lucky wheel prize',
                'verbose_name_plural': 'Lucky wheel prizes',
                'ordering': ('order', 'id'),
            },
        ),
        migrations.CreateModel(
            name='LuckyWheelSpin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=30, verbose_name='Mobile number')),
                ('phone_normalized', models.CharField(db_index=True, help_text='Digits only, used to prevent duplicate spins.', max_length=20, verbose_name='Normalized phone')),
                ('prize_title', models.CharField(blank=True, help_text='Stored at spin time so admin prize edits do not rewrite history.', max_length=200, verbose_name='Prize title (snapshot)')),
                ('prize_code', models.CharField(blank=True, max_length=64, verbose_name='Coupon code (snapshot)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('prize', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='spins', to='projects.luckywheelprize', verbose_name='Prize')),
            ],
            options={
                'verbose_name': 'Lucky wheel spin',
                'verbose_name_plural': 'Lucky wheel spins',
                'ordering': ('-created_at',),
            },
        ),
        migrations.RunPython(seed_prizes, unseed_prizes),
    ]


from django.db import models
from apps.bom.material.models import Material
from apps.bom.initialparts.models import InitialParts
from apps.auth.users.models import UserProfile


class Screw(models.Model):

    ORDER_STATUS = (
        (0, '已取消'),
        (1, '待递交'),
        (2, '已完结')
    )

    MISTAKE_LIST = (
        (0, '正常'),
        (1, '重复递交'),
        (2, '已存此编码物料'),
        (3, '配件种类缺螺丝'),
        (4, '创建初始物料出错'),
        (5, '非错误订单不要修复'),
    )

    PROCESSTAG = (
        (0, '未标记'),
        (1, '已标记'),
    )

    MATERIAL_LIST = (
        ('CS', '碳钢'),
        ('SS', '不锈钢'),
        ('BR', '铜质'),
    )

    HEAD_TYPE_LIST = (
        ('B', '球面圆柱B头'),
        ('K', '平K头'),
        ('C', '圆柱C头'),
        ('F', '沉头'),
        ('H', '六角头'),
        ('HW', '六角头带垫圈'),
        ('O', '半沉O头'),
        ('P', '平元P头'),
        ('R', '半元R头'),
        ('PW', '平元头带垫圈'),
        ('T', '大扁T头'),
        ('V', '蘑菇头'),
        ('TW', '伞头'),
    )

    TOOTH_TYPE_LIST = (
        ('A', '自攻尖尾疏A牙'),
        ('AB', '自攻尖尾密AB牙'),
        ('B', '自攻平尾疏B牙'),
        ('C', '自攻平尾密C牙'),
        ('P', '双牙丝P牙'),
        ('HL', '高低HL牙'),
        ('U', '玻璃牙纹U牙'),
        ('T', '自攻平尾切脚T牙'),
        ('AT', '自攻尖尾切脚AT牙'),
        ('M', '机械牙M牙'),
        ('BBT', 'B型三角牙'),
        ('CCT', 'C型三角牙'),
        ('PTT', 'P型三角牙'),
        ('STT', 'S型三角牙'),
    )

    HEAT_TREATED_LIST = (
        ('NT', '正火'),
        ('CA', '退火'),
        ('SHT', '固溶热'),
        ('SS', '固溶'),
        ('QT', '淬火'),
        ('B', '钎焊'),
    )

    FINISH_LIST = (
        ('DAC', '达克罗'),
        ('ZU', '蓝锌'),
        ('ZB', '黑锌'),
        ('ZC', '五彩锌'),
        ('ZI', '白锌'),
        ('BL', '氧化黑色'),
        ('GD', '氧化金色'),
        ('RU', '红铜'),
        ('YU', '黄铜'),
        ('CN', '镀铜底镍'),
        ('DT', '哑锡'),
        ('TP', '锡铅合金'),
        ('SA', '沙阳极'),
        ('NI', '亮镍'),
        ('EN', '无电解镍'),
        ('CR', '亮铬'),
        ('ET', '亮锡'),
        ('PS', '钝化'),
        ('AU', '镀金'),
        ('AG', '镀银'),
        ('TI', '镀钛'),
        ('ZF', '镀镉'),
        ('CH', '铬酸盐'),
        ('X', '素材'),
        ('EF', '电泳漆'),
        ('OT', '其他'),
    )

    SLOT_LIST = (
        ('+', '十字槽'),
        ('-', '一字槽'),
        ('△', '三角槽'),
        ('□', '内方槽'),
        ('T', '菊花槽'),
        ('HS', '内六角'),
        ('PZ', '米字槽'),
        ('+-', '十一槽'),
        ('Y', 'Y型槽'),
        ('H', '工字槽'),
        ('L', '止退花齿'),
    )

    name = models.CharField(null=True, blank=True, max_length=120, verbose_name='螺丝名称', help_text='螺丝名称')
    code = models.CharField(max_length=90, unique=True, null=True, blank=True, verbose_name='螺丝编码', help_text='螺丝编码')
    material = models.CharField(choices=MATERIAL_LIST, max_length=10, verbose_name='材质', help_text='材质')
    diameter = models.IntegerField(verbose_name='牙径', help_text='牙径')
    length = models.IntegerField(verbose_name='长度', help_text='长度')

    head_type = models.CharField(choices=HEAD_TYPE_LIST, max_length=10, verbose_name='螺丝头型', help_text='螺丝头型')
    tooth_type = models.CharField(choices=TOOTH_TYPE_LIST, max_length=10, verbose_name='螺丝牙型', help_text='螺丝牙型')
    heat_treated = models.CharField(choices=HEAT_TREATED_LIST, null=True, blank=True, max_length=10, verbose_name='热处理', help_text='热处理')
    finish = models.CharField(choices=FINISH_LIST, max_length=10, verbose_name='表面处理', help_text='表面处理')

    initial_parts = models.ForeignKey(InitialParts, on_delete=models.CASCADE, null=True, blank=True, verbose_name='初始物料', help_text='初始物料')
    slot_type = models.CharField(choices=SLOT_LIST, max_length=10, verbose_name='开槽类型', help_text='开槽类型')
    memo = models.CharField(max_length=90, unique=True, null=True, blank=True, verbose_name='特殊备注', help_text='特殊备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-标准库-螺丝'
        verbose_name_plural = verbose_name
        db_table = 'bom_standardlabrary_screw'

    def __str__(self):
        return self.name


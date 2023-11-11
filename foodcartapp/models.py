from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class OrderQuerySet(models.QuerySet):
    def restaurants_for_order(self, order_id):
        order = self.get(pk=order_id)
        restaurant = order.restaurant
        if restaurant:
            return Restaurant.objects.filter(pk=restaurant.pk).distinct()
        else:
            products = order.items.all().values_list('product_id', flat=True)
            restaurants = Restaurant.objects.filter(menu_items__product_id__in=products).distinct()
            for product_id in products:
                restaurants = restaurants.filter(menu_items__product_id=product_id)
            return restaurants.distinct()


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    restaurants = models.ManyToManyField(Restaurant,
                                         related_name='products',
                                         verbose_name='рестораны')

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):

    CHOICES = (
        (1, 'Необработанный'),
        (2, 'Обрабатывается'),
        (3, 'Доставляет курьер'),
        (4, 'Выполнен'),
    )

    status = models.PositiveIntegerField(verbose_name='Cтатус',
                                         choices=CHOICES,
                                         default=1,
                                         db_index=True)

    PAYMENT_CHOICES = (
        (1, 'Наличностью'),
        (2, 'Электронно'),
    )

    payment_method = models.PositiveIntegerField(choices=PAYMENT_CHOICES,
                                                 db_index=True,
                                                 verbose_name='Способ оплаты')

    registered_at = models.DateTimeField(default=timezone.now,
                                         db_index=True,
                                         verbose_name='Время и дата создания заказа')

    called_at = models.DateTimeField(null=True,
                                     blank=True,
                                     db_index=True,
                                     verbose_name='Время и дата звонка менеджера')

    delivered_at = models.DateTimeField(null=True,
                                        blank=True,
                                        db_index=True,
                                        verbose_name='Время и дата доставки')

    firstname = models.CharField(max_length=100,
                                 verbose_name='Имя')
    lastname = models.CharField(max_length=100,
                                blank=True,
                                verbose_name='Фамилия')
    phonenumber = PhoneNumberField(region='RU',
                                   verbose_name='Номер телефона'
                                   )
    address = models.CharField(max_length=200,
                               verbose_name='Адрес доставки',
                               db_index=True)

    comment = models.TextField(max_length=200,
                               blank=True,
                               verbose_name='Комментарий')

    restaurant = models.ForeignKey(Restaurant,
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   blank=True,
                                   verbose_name='Ресторан')

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return self.firstname, self.status, self.phonenumber, self.address


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        verbose_name="заказ",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='продукт',
    )

    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    quantity = models.IntegerField(verbose_name='Количество',
                                   validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'

    def __str__(self):
        return f"{self.order.firstname} - {self.product.name}"

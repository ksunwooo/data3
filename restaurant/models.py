from django.db import models
from django.core.exceptions import ValidationError


class Article(models.Model):
    titel = models.CharField(max_length = 100 , db_index=True)
    preview_image = models.ImageField(null=True, blank=True)
    content = models.TextField()
    show_at_index = models.BooleanField(default=False) # 기본값은 표시안함
    is_published = models.BooleanField(default=False) # 칼럼을 사용자에게 노출할지 여부
    created_at = models.DateTimeField("생성일",auto_now_add=True)
    modified_at = models.DateTimeField("수정일",auto_now=True)

    class Meta:
        verbose_name = "칼럼"
        verbose_name_plural = "칼럼s"

    def str(self):
        return f"{self.id} - {self.title}"


class Restaurant(models.Model):
    name = models.CharField("이름", max_length=100, db_index=True)
    branch_name = models.CharField(
        "지점", max_length=100, db_index=True, null=True, blank=True
    )
    description = models.TextField("설명", null=True, blank=True)
    address = models.CharField("주소", max_length=255, db_index=True)
    feature = models.CharField("특징", max_length=255, null=True, blank=True)
    is_closed = models.BooleanField("폐업여부", default=False)
    latitude = models.DecimalField(
        "위도",
        max_digits=16, # 소수점포함 숫자자릿점 38.01215654
        decimal_places=12, # 소수점 이하 자릿수 정수부: 소수부
        db_index=True,
        default="0.0000",
    )
    longitude = models.DecimalField(
        "경도",
        max_digits=16,
        decimal_places=12,
        db_index=True,
        default="0.0000",
    )
    phone = models.CharField(
        "전화번호", max_length=16,
        help_text="E.164 포멧" # 예: +821012345678
    )
    rating = models.DecimalField(
        "평점",
        max_digits=3, # 유효숫자3 -> 9.99, 123, 0.0123
        decimal_places=2, # 소수점2자리 9.99, 10.99, 999.99
        default=0.00,
        db_index=True,
    )
    rating_count = models.PositiveIntegerField("평가수", default=0,)#좋아요
    #영업시간
    start_time = models.TimeField("영업시작시간", null=True, blank=True)
    end_time = models.TimeField("영업종료시간", null=True, blank=True)
    last_order_time = models.TimeField("마지막주문시간", null=True, blank=True)
    category = models.ForeignKey(
        "restaurantCategory",
        on_delete=models.SET_NULL, #참ㅈ된 카테고리 삭제시 null로 설정, 데이터보존
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField(
        "Tag",blank=True,) # 다대다 관계, 여러개의 태그를 가질 수 있음 N:M

    region = models.ForeignKey(
        "지역",
        on_delete=models.SET_NULL, # 참조된 지역 삭제시 null로 설정, 데이터보존
        null=True,
        blank=True,
        verbose_name="지역", # 필드 이름 설정
        related_name="restaurants", # 역참조 이름 설정
    )
    # 레스토랑 지역 region.restaurants.all()로 접근 가능

    class Meta:
        verbose_name = "레스토랑"
        verbose_name_plural = "레스토랑s"

        def __str__(self):
            return f"{self.name} {self.branch_name or '본점'}" if self.branch_name else self.name
        # 지정명 있으면 지정명을 반환, 없으면 식당이름
        # 본스테이크 강남점, 본스테이크

class CuisineType(models.Model):
    name = models.CharField("이름", max_length=20, db_index=True)

    class Meta:
        verbose_name = "요리종류"
        verbose_name_plural = "요리종류s"

        def __str__(self):
            return self.name

class RestaurantCategory(models.Model):
    name = models.CharField("이름", max_length=20, db_index=True)

    class Meta:
        verbose_name = "레스토랑 카테고리"
        verbose_name_plural = "레스토랑 카테고리s"

        def __str__(self):
            return self.name

class RestaurantCategry(models.Model):
    name = models.CharField("이름", max_length=20, db_index=True)

    CuisineType = models.ForeignKey(
        "CuisineType",
        on_delete=models.CASCADE, # 참조된 요리종류 삭제시 null로
        null=True,
        blank=True,
    )
    class Meta:
        verbose_name = "레스토랑 카테고리"
        verbose_name_plural = "레스토랑 카테고리s"

        def __str__(self):
            return self.name

class RestrantImage(models.Model):
    restaurant = models.ForeignKey(
        "Restaurant",
        on_delete=models.CASCADE) # 참조된 레스토랑 삭제시 이미지도 삭제
    is_representative = models.BooleanField("대표이미지 여부", default=False) # 대표이미지 여부 체크안하고 업데이트 했는데체크하면 대표이미지로 변경
    name = models.CharField("이름", max_length=100, db_index=True, null=True, blank=True) # 이미지 이름
    image = models.ImageField("이미지", upload_to="restaurant")
    order = models.PositiveIntegerField("순서", default=0) # 이미지 순서
    created_at = models.DateTimeField("생성일", auto_now_add=True, dbindex=True) # 생성일
    updateed_at = models.DateTimeField("수정일", auto_now=True, dbindex=True) # 수정일

    class Meta:
        verbose_name = "레스토랑 카테고리"
        verbose_name_plural = "레스토랑 카테고리s"

    def __str__(self):
        return f"{self.id}:{self.image}"

    # 대표이미지 2개 이상 저장하지 못하도록 막는 코드 작성
    def clean(self):
        images = self.restaurant.restrantimage_set.filter(is_representative=True)
        #.restrantimage_set: 역참조, 레스토랑에 속한 이미지들
        #.filter(is_representative=True): 대표이미지들만 필터링

        if self.is_representative and images.exists() and not images.filter(id=self.id).exists():
            raise ValidationError("대표이미지는 하나만 설정할 수 있습니다.")

class RestaurantMenu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE) # 참조된 레스토랑 삭제시 메뉴도 삭제
    name = models.CharField("이름", max_length=100, db_index=True) # 메뉴 이름
    price = models.PositiveBigIntegerField("가격", default=0) # 메뉴 가격
    image =
    created_at
    updated_at

    class Meta:
        verbose_name = "레스토랑 카테고리"
        verbose_name_plural = "레스토랑 카테고리s"

        def __str__(self):
            return self.name

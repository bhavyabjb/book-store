import datetime as dt

from app.models.address import Address as AddressModel
from app.models.author import Author as AuthorModel
from app.models.book import Book as BookModel
from app.models.category import Category as CategoryModel
from app.models.order import Order as OrderModel
from app.models.order import OrderItem as OrderItemModel
from app.models.review import Review as ReviewModel
from app.schemas.address import Address as AddressSchema
from app.schemas.catalog import Author as AuthorSchema
from app.schemas.catalog import BookDetail, BookSummary
from app.schemas.catalog import Category as CategorySchema
from app.schemas.order import Order as OrderSchema
from app.schemas.order import OrderItem as OrderItemSchema
from app.schemas.review import Review as ReviewSchema


def author_to_schema(author: AuthorModel) -> AuthorSchema:
    return AuthorSchema(id=author.id, name=author.name, bio=author.bio, photo_url=author.photo_url)


def category_to_schema(category: CategoryModel) -> CategorySchema:
    return CategorySchema(id=category.id, name=category.name, slug=category.slug, parent_id=category.parent_id)


def book_to_summary(book: BookModel) -> BookSummary:
    delivery_date = dt.date.today() + dt.timedelta(days=book.delivery_days)
    return BookSummary(
        id=book.id,
        slug=book.slug,
        title=book.title,
        author=author_to_schema(book.author),
        description=book.description,
        price=float(book.price),
        format=book.format.value,
        cover_image_url=book.cover_image_url,
        tags=[t.tag for t in book.tags],
        rating_avg=book.rating_avg,
        delivery_date=delivery_date,
    )


def book_to_detail(book: BookModel) -> BookDetail:
    summary = book_to_summary(book)
    return BookDetail(
        **summary.model_dump(),
        publisher=book.publisher,
        language=book.language,
        isbn=book.isbn,
        back_cover_image_url=book.back_cover_image_url,
        units_sold=book.units_sold,
        category=category_to_schema(book.category),
    )


def review_to_schema(review: ReviewModel) -> ReviewSchema:
    return ReviewSchema(
        id=review.id,
        book_id=review.book_id,
        reviewer_name=review.reviewer_name,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
    )


def address_to_schema(address: AddressModel) -> AddressSchema:
    return AddressSchema(
        id=address.id,
        first_name=address.first_name,
        last_name=address.last_name,
        line1=address.line1,
        city=address.city,
        state=address.state,
        pin=address.pin,
        country=address.country,
        phone=address.phone,
        email=address.email,
        is_default=address.is_default,
    )


def order_item_to_schema(item: OrderItemModel) -> OrderItemSchema:
    return OrderItemSchema(
        book=book_to_summary(item.book),
        quantity=item.quantity,
        unit_price=float(item.unit_price),
    )


def order_to_schema(order: OrderModel) -> OrderSchema:
    return OrderSchema(
        id=order.id,
        status=order.status.value,
        total=float(order.total),
        placed_at=order.placed_at,
        cancel_by=order.cancel_by,
        items=[order_item_to_schema(i) for i in order.items],
        address=address_to_schema(order.address),
        subtotal=float(order.subtotal),
        tax=float(order.tax),
        delivery_charge=float(order.delivery_charge),
        discount=float(order.discount),
        coupon_code=order.coupon_code,
        gift_points_redeemed=order.gift_points_redeemed,
    )

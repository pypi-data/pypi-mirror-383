from __future__ import annotations

from typing import Literal, Optional, cast

from fastapi import Depends, Header, Request, Response, status
from starlette.responses import JSONResponse

from svc_infra.apf_payments.schemas import (
    CaptureIn,
    CustomerOut,
    CustomerUpsertIn,
    IntentCreateIn,
    IntentListFilter,
    IntentOut,
    InvoiceCreateIn,
    InvoiceLineItemIn,
    InvoiceOut,
    InvoicesListFilter,
    PaymentMethodAttachIn,
    PaymentMethodOut,
    PriceCreateIn,
    PriceOut,
    ProductCreateIn,
    ProductOut,
    RefundIn,
    StatementRow,
    SubscriptionCreateIn,
    SubscriptionOut,
    SubscriptionUpdateIn,
    TransactionRow,
    UsageRecordIn,
)
from svc_infra.apf_payments.service import PaymentsService
from svc_infra.api.fastapi.db.sql.session import SqlSessionDep
from svc_infra.api.fastapi.dual import protected_router, public_router, service_router, user_router
from svc_infra.api.fastapi.dual.router import DualAPIRouter
from svc_infra.api.fastapi.pagination import (
    Paginated,
    cursor_pager,
    cursor_window,
    sort_by,
    use_pagination,
)

_TX_KINDS = {"payment", "refund", "fee", "payout", "capture"}


def _tx_kind(kind: str) -> Literal["payment", "refund", "fee", "payout", "capture"]:
    if kind not in _TX_KINDS:
        raise ValueError(f"Unknown ledger kind: {kind!r}")
    return cast(Literal["payment", "refund", "fee", "payout", "capture"], kind)


# --- deps ---
async def get_service(session: SqlSessionDep) -> PaymentsService:
    return PaymentsService(session=session)


# --- routers grouped by auth posture (same prefix is fine; FastAPI merges) ---
def build_payments_routers(prefix: str = "/payments") -> list[DualAPIRouter]:
    routers: list[DualAPIRouter] = []

    # USER endpoints (require logged-in user)
    user = user_router(prefix=prefix, tags=["payments"])

    # SERVICE endpoints (api key only)
    svc = service_router(prefix=prefix, tags=["payments"])

    # PROTECTED endpoints (user OR api key)
    prot = protected_router(prefix=prefix, tags=["payments"])

    @user.post("/customers", response_model=CustomerOut, name="payments_upsert_customer")
    async def upsert_customer(data: CustomerUpsertIn, svc: PaymentsService = Depends(get_service)):
        # Upsert semantics: keep 200 OK (creation vs update is ambiguous here).
        out = await svc.ensure_customer(data)
        await svc.session.flush()
        return out

    @user.post(
        "/intents",
        response_model=IntentOut,
        name="payments_create_intent",
        status_code=status.HTTP_201_CREATED,
    )
    async def create_intent(
        data: IntentCreateIn,
        request: Request,
        response: Response,
        svc: PaymentsService = Depends(get_service),
    ):
        out = await svc.create_intent(user_id=None, data=data)
        await svc.session.flush()

        # Location → canonical GET for this resource
        location = request.url_for("payments_get_intent", provider_intent_id=out.provider_intent_id)
        response.headers["Location"] = str(location)
        return out

    routers.append(user)

    @prot.post(
        "/intents/{provider_intent_id}/confirm",
        response_model=IntentOut,
        name="payments_confirm_intent",
    )
    async def confirm_intent(provider_intent_id: str, svc: PaymentsService = Depends(get_service)):
        out = await svc.confirm_intent(provider_intent_id)
        await svc.session.flush()
        return out

    @prot.post(
        "/intents/{provider_intent_id}/cancel",
        response_model=IntentOut,
        name="payments_cancel_intent",
    )
    async def cancel_intent(provider_intent_id: str, svc: PaymentsService = Depends(get_service)):
        out = await svc.cancel_intent(provider_intent_id)
        await svc.session.flush()
        return out

    @prot.post(
        "/intents/{provider_intent_id}/refund",
        response_model=IntentOut,
        name="payments_refund_intent",
    )
    async def refund_intent(
        provider_intent_id: str, data: RefundIn, svc: PaymentsService = Depends(get_service)
    ):
        out = await svc.refund(provider_intent_id, data)
        await svc.session.flush()
        return out

    @prot.get(
        "/transactions",
        response_model=Paginated[TransactionRow],
        name="payments_list_transactions",
        dependencies=[Depends(cursor_pager(default_limit=50, max_limit=200))],
    )
    async def list_transactions(svc: PaymentsService = Depends(get_service)):
        from sqlalchemy import select

        from svc_infra.apf_payments.models import LedgerEntry

        rows = (await svc.session.execute(select(LedgerEntry))).scalars().all()
        rows_sorted = sort_by(rows, key=lambda e: e.ts, desc=True)

        ctx = use_pagination()
        window, next_cursor = cursor_window(
            rows_sorted,
            cursor=ctx.cursor,
            limit=ctx.limit,
            key=lambda e: int(e.ts.timestamp()),
            descending=True,
        )

        items = [
            TransactionRow(
                id=e.id,
                ts=e.ts.isoformat(),
                type=_tx_kind(e.kind),
                amount=int(e.amount),
                currency=e.currency,
                status=e.status,
                provider=e.provider,
                provider_ref=e.provider_ref or "",
                user_id=e.user_id,
            )
            for e in window
        ]
        return ctx.wrap(items, next_cursor=next_cursor)

    routers.append(prot)

    # PUBLIC webhooks
    pub = public_router(prefix=prefix, tags=["payments"])

    @pub.post("/webhooks/{provider}", name="payments_webhook")
    async def webhooks(
        provider: str,
        request: Request,
        svc: PaymentsService = Depends(get_service),
        signature: Optional[str] = Header(None, alias="Stripe-Signature"),
    ):
        payload = await request.body()
        out = await svc.handle_webhook(provider.lower(), signature, payload)
        await svc.session.flush()
        return JSONResponse(out)

    @user.post(
        "/methods/attach",
        response_model=PaymentMethodOut,
        name="payments_attach_method",
        status_code=status.HTTP_201_CREATED,
    )
    async def attach_method(
        data: PaymentMethodAttachIn, svc: PaymentsService = Depends(get_service)
    ):
        # No canonical GET by id; return 201 Created without Location.
        out = await svc.attach_payment_method(data)
        await svc.session.flush()
        return out

    @prot.get(
        "/methods",
        response_model=Paginated[PaymentMethodOut],
        name="payments_list_methods",
        dependencies=[Depends(cursor_pager(default_limit=50, max_limit=200))],
    )
    async def list_methods(
        customer_provider_id: str,
        svc: PaymentsService = Depends(get_service),
    ):
        methods = await svc.list_payment_methods(customer_provider_id)
        methods_sorted = sort_by(
            sort_by(methods, key=lambda m: m.provider_method_id or "", desc=False),
            key=lambda m: m.is_default,
            desc=True,
        )
        ctx = use_pagination()
        window, next_cursor = cursor_window(
            methods_sorted,
            cursor=ctx.cursor,
            limit=ctx.limit,
            key=lambda m: m.provider_method_id or "",
            descending=False,
        )
        return ctx.wrap(window, next_cursor=next_cursor)

    @prot.post("/methods/{provider_method_id}/detach", name="payments_detach_method")
    async def detach_method(provider_method_id: str, svc: PaymentsService = Depends(get_service)):
        await svc.detach_payment_method(provider_method_id)
        await svc.session.flush()
        return {"ok": True}

    @prot.post("/methods/{provider_method_id}/default", name="payments_set_default_method")
    async def set_default_method(
        provider_method_id: str,
        customer_provider_id: str,
        svc: PaymentsService = Depends(get_service),
    ):
        await svc.set_default_payment_method(customer_provider_id, provider_method_id)
        await svc.session.flush()
        return {"ok": True}

    # PRODUCTS/PRICES
    @svc.post(
        "/products",
        response_model=ProductOut,
        name="payments_create_product",
        status_code=status.HTTP_201_CREATED,
    )
    async def create_product(data: ProductCreateIn, svc: PaymentsService = Depends(get_service)):
        # No product GET endpoint; 201 without Location.
        out = await svc.create_product(data)
        await svc.session.flush()
        return out

    @svc.post(
        "/prices",
        response_model=PriceOut,
        name="payments_create_price",
        status_code=status.HTTP_201_CREATED,
    )
    async def create_price(data: PriceCreateIn, svc: PaymentsService = Depends(get_service)):
        # No price GET endpoint; 201 without Location.
        out = await svc.create_price(data)
        await svc.session.flush()
        return out

    # SUBSCRIPTIONS
    @prot.post(
        "/subscriptions",
        response_model=SubscriptionOut,
        name="payments_create_subscription",
        status_code=status.HTTP_201_CREATED,
    )
    async def create_subscription(
        data: SubscriptionCreateIn, svc: PaymentsService = Depends(get_service)
    ):
        # No subscription GET endpoint; 201 without Location.
        out = await svc.create_subscription(data)
        await svc.session.flush()
        return out

    @prot.post(
        "/subscriptions/{provider_subscription_id}",
        response_model=SubscriptionOut,
        name="payments_update_subscription",
    )
    async def update_subscription(
        provider_subscription_id: str,
        data: SubscriptionUpdateIn,
        svc: PaymentsService = Depends(get_service),
    ):
        out = await svc.update_subscription(provider_subscription_id, data)
        await svc.session.flush()
        return out

    @prot.post(
        "/subscriptions/{provider_subscription_id}/cancel",
        response_model=SubscriptionOut,
        name="payments_cancel_subscription",
    )
    async def cancel_subscription(
        provider_subscription_id: str,
        at_period_end: bool = True,
        svc: PaymentsService = Depends(get_service),
    ):
        out = await svc.cancel_subscription(provider_subscription_id, at_period_end)
        await svc.session.flush()
        return out

    # INVOICES
    @prot.post(
        "/invoices",
        response_model=InvoiceOut,
        name="payments_create_invoice",
        status_code=status.HTTP_201_CREATED,
    )
    async def create_invoice(
        data: InvoiceCreateIn,
        request: Request,
        response: Response,
        svc: PaymentsService = Depends(get_service),
    ):
        out = await svc.create_invoice(data)
        await svc.session.flush()

        # Location → canonical GET for invoice
        location = request.url_for(
            "payments_get_invoice", provider_invoice_id=out.provider_invoice_id
        )
        response.headers["Location"] = str(location)
        return out

    @prot.post(
        "/invoices/{provider_invoice_id}/finalize",
        response_model=InvoiceOut,
        name="payments_finalize_invoice",
    )
    async def finalize_invoice(
        provider_invoice_id: str, svc: PaymentsService = Depends(get_service)
    ):
        out = await svc.finalize_invoice(provider_invoice_id)
        await svc.session.flush()
        return out

    @prot.post(
        "/invoices/{provider_invoice_id}/void",
        response_model=InvoiceOut,
        name="payments_void_invoice",
    )
    async def void_invoice(provider_invoice_id: str, svc: PaymentsService = Depends(get_service)):
        out = await svc.void_invoice(provider_invoice_id)
        await svc.session.flush()
        return out

    @prot.post(
        "/invoices/{provider_invoice_id}/pay",
        response_model=InvoiceOut,
        name="payments_pay_invoice",
    )
    async def pay_invoice(provider_invoice_id: str, svc: PaymentsService = Depends(get_service)):
        out = await svc.pay_invoice(provider_invoice_id)
        await svc.session.flush()
        return out

    # INTENTS: get/hydrate
    @prot.get("/intents/{provider_intent_id}", response_model=IntentOut, name="payments_get_intent")
    async def get_intent(provider_intent_id: str, svc: PaymentsService = Depends(get_service)):
        return await svc.get_intent(provider_intent_id)

    # STATEMENTS (rollup)
    @svc.get(
        "/statements/daily", response_model=list[StatementRow], name="payments_daily_statements"
    )
    async def daily_statements(
        date_from: str | None = None,
        date_to: str | None = None,
        svc: PaymentsService = Depends(get_service),
    ):
        return await svc.daily_statements_rollup(date_from, date_to)

    # ===== Intents: capture & list =====
    @prot.post(
        "/intents/{provider_intent_id}/capture",
        response_model=IntentOut,
        name="payments_capture_intent",
    )
    async def capture_intent(
        provider_intent_id: str,
        data: CaptureIn,
        svc: PaymentsService = Depends(get_service),
    ):
        out = await svc.capture_intent(provider_intent_id, data)
        await svc.session.flush()
        return out

    @prot.get(
        "/intents",
        response_model=Paginated[IntentOut],
        name="payments_list_intents",
        dependencies=[Depends(cursor_pager(default_limit=50, max_limit=200))],
    )
    async def list_intents_endpoint(
        customer_provider_id: Optional[str] = None,
        status: Optional[str] = None,
        svc: PaymentsService = Depends(get_service),
    ):
        ctx = use_pagination()
        items, next_cursor = await svc.list_intents(
            IntentListFilter(
                customer_provider_id=customer_provider_id,
                status=status,
                limit=ctx.limit,
                cursor=ctx.cursor,
            )
        )
        return ctx.wrap(items, next_cursor=next_cursor)

    # ===== Invoices: lines/list/get/preview =====
    @prot.post(
        "/invoices/{provider_invoice_id}/lines",
        name="payments_add_invoice_line_item",
        status_code=status.HTTP_201_CREATED,
    )
    async def add_invoice_line(
        provider_invoice_id: str,
        data: InvoiceLineItemIn,
        svc: PaymentsService = Depends(get_service),
    ):
        # Stripe invoice items attach to customer; no canonical GET for the created line.
        out = await svc.add_invoice_line_item(data)
        await svc.session.flush()
        return {"ok": True, **out}

    @prot.get(
        "/invoices",
        response_model=Paginated[InvoiceOut],
        name="payments_list_invoices",
        dependencies=[Depends(cursor_pager(default_limit=50, max_limit=200))],
    )
    async def list_invoices_endpoint(
        customer_provider_id: Optional[str] = None,
        status: Optional[str] = None,
        svc: PaymentsService = Depends(get_service),
    ):
        ctx = use_pagination()
        items, next_cursor = await svc.list_invoices(
            InvoicesListFilter(
                customer_provider_id=customer_provider_id,
                status=status,
                limit=ctx.limit,
                cursor=ctx.cursor,
            )
        )
        return ctx.wrap(items, next_cursor=next_cursor)

    @prot.get(
        "/invoices/{provider_invoice_id}", response_model=InvoiceOut, name="payments_get_invoice"
    )
    async def get_invoice_endpoint(
        provider_invoice_id: str, svc: PaymentsService = Depends(get_service)
    ):
        return await svc.get_invoice(provider_invoice_id)

    @prot.post("/invoices/preview", response_model=InvoiceOut, name="payments_preview_invoice")
    async def preview_invoice_endpoint(
        customer_provider_id: str,
        subscription_id: Optional[str] = None,
        svc: PaymentsService = Depends(get_service),
    ):
        return await svc.preview_invoice(customer_provider_id, subscription_id)

    # ===== Metered usage =====
    @prot.post(
        "/usage_records",
        name="payments_create_usage_record",
        status_code=status.HTTP_201_CREATED,
    )
    async def create_usage_record_endpoint(
        data: UsageRecordIn, svc: PaymentsService = Depends(get_service)
    ):
        out = await svc.create_usage_record(data)
        await svc.session.flush()
        return out

    routers.append(svc)
    routers.append(pub)
    return routers

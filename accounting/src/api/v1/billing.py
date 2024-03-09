from collections import defaultdict

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from starlette.responses import RedirectResponse

from accounting.src.api.dependencies import SessionDep
from accounting.src.api.dependencies import check_permissions
from accounting.src.repositories.account import AccountRepository
from accounting.src.repositories.analytics import AnalyticsRepository
from accounting.src.repositories.billing_cycle import BillingCycleRepository
from accounting.src.repositories.transaction import TransactionRepository
from accounting.src.services.billing import complete_billing_cycles
from packages.permissions.role import Role

router = APIRouter()
templates = Jinja2Templates(directory='accounting/src/templates/')


@router.get('/account/', response_class=HTMLResponse)
async def get_account_info(db: SessionDep, request: Request):
    account = await AccountRepository(db).get_user_account(request.user.id)
    active_billing_cycle = await BillingCycleRepository(db).get_active_for_account(account.id)
    if not account:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    transactions = await TransactionRepository(db).get_all_for_account(account.id)

    transactions_per_day = defaultdict(list)
    for transaction in transactions:
        transactions_per_day[transaction.processing_dt.date()].append(transaction)

    return templates.TemplateResponse(
        request=request,
        name='billing/account.html',
        context={
            'account': account,
            'transactions_per_day': transactions_per_day,
            'active_billing_cycle': active_billing_cycle,
        },
    )


@router.get(
    '/transactions/',
    response_class=HTMLResponse,
    dependencies=[Depends(check_permissions(Role.ADMIN))],
)
async def get_all_transactions(
    db: SessionDep,
    request: Request,
):
    transactions = await TransactionRepository(db).get_all()

    return templates.TemplateResponse(
        request=request,
        name='billing/transactions.html',
        context={
            'transactions': transactions,
        },
    )


@router.post(
    '/billing_cycle/complete/',
    dependencies=[Depends(check_permissions(Role.ADMIN))],
)
async def complete_billing_cycle(
    db: SessionDep,
    request: Request,
):
    await complete_billing_cycles(db)
    return RedirectResponse(
        request.url_for('get_account_info'),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get(
    '/analytics/',
    response_class=HTMLResponse,
    dependencies=[Depends(check_permissions(Role.ADMIN))],
)
async def get_analytic_info(
    db: SessionDep,
    request: Request,
):
    repo = AnalyticsRepository(db)
    return templates.TemplateResponse(
        request=request,
        name='billing/analytics.html',
        context={
            'earned_today': await repo.get_earned_today(),
            'workers_with_negative_balance': await repo.get_workers_count_with_negative_balance(),
            'most_expensive_task_per_day': await repo.get_most_expensive_task_per_day(),
            'most_expensive_task_per_week': await repo.get_most_expensive_task_per_week(),
            'most_expensive_task_last_month': await repo.get_most_expensive_task_last_month(),
        },
    )

"""Aviso por correo a los administradores de plataforma de cada comunidad nueva (HU-46)."""

from datetime import datetime
from html import escape

from entrevecinos.application.mail.email_quota import EmailQuota
from entrevecinos.application.users.ports import OutgoingEmail, UserRepository
from entrevecinos.domain.communities.entities import Community
from entrevecinos.domain.mail.errors import EmailQuotaExceeded
from entrevecinos.domain.mail.quota import QUOTA_TIMEZONE
from entrevecinos.domain.users.entities import User


class CommunityNotices:
    """Prepara los avisos y reserva una plaza del cupo por cada uno.

    Sin cupo no se prepara ninguno más: la comunidad se crea igual, porque el aviso nunca debe
    impedirlo. `EmailQuota` ya registra el bloqueo.
    """

    def __init__(self, users: UserRepository, quota: EmailQuota, web_public_url: str) -> None:
        self._users = users
        self._quota = quota
        self._web_public_url = web_public_url.rstrip("/")

    def community_created(self, community: Community, creator: User) -> list[OutgoingEmail]:
        """Un aviso por `platform_admin` si la comunidad queda pendiente; ninguno si está activa.

        A diferencia de los avisos a vecinos (TK-106), incluye el correo y el teléfono del
        creador: los destinatarios son quienes revisan la comunidad.
        """
        if community.is_active:
            return []
        link = f"{self._web_public_url}/admin/comunidades#comunidad-{community.id}"
        messages: list[OutgoingEmail] = []
        for admin in self._users.list_platform_admins():
            if admin.id == creator.id:
                continue
            if not self._reserve():
                break
            messages.append(_community_created(admin, creator, community, link))
        return messages

    def _reserve(self) -> bool:
        try:
            self._quota.reserve()
        except EmailQuotaExceeded:
            return False
        return True


def _date(value: datetime) -> str:
    return value.astimezone(QUOTA_TIMEZONE).strftime("%d/%m/%Y")


def _community_created(
    admin: User, creator: User, community: Community, link: str
) -> OutgoingEmail:
    community_rows = [
        ("Nombre", community.name),
        ("Descripción", community.description or "Sin descripción"),
        ("Ciudad", community.city or "—"),
        ("Código postal", community.postal_code or "—"),
        ("Creada el", _date(community.created_at)),
    ]
    creator_rows = [
        ("Nombre", creator.full_name),
        ("Correo", creator.email),
        ("Teléfono", creator.phone or "Sin teléfono"),
        ("Alta en EntreVecinos", _date(creator.created_at)),
    ]
    intro = (
        f"{creator.full_name} ha creado la comunidad {community.name} "
        "y está pendiente de aprobación."
    )
    footer = "Recibes este correo porque eres administrador de EntreVecinos."

    def text_block(title: str, rows: list[tuple[str, str]]) -> str:
        return f"{title}\n" + "".join(f"- {label}: {value}\n" for label, value in rows)

    def html_block(title: str, rows: list[tuple[str, str]]) -> str:
        items = "".join(
            f"<li><strong>{escape(label)}:</strong> {escape(value)}</li>" for label, value in rows
        )
        return f"<h2>{escape(title)}</h2><ul>{items}</ul>"

    text = (
        f"Hola, {admin.full_name}:\n\n{intro}\n\n"
        f"{text_block('Comunidad', community_rows)}\n"
        f"{text_block('Creada por', creator_rows)}\n"
        f"Apruébala o recházala aquí:\n\n{link}\n\n{footer}\n"
    )
    html = (
        f"<p>Hola, {escape(admin.full_name)}:</p><p>{escape(intro)}</p>"
        f"{html_block('Comunidad', community_rows)}"
        f"{html_block('Creada por', creator_rows)}"
        f'<p><a href="{escape(link)}">Revisar comunidades pendientes</a></p>'
        f"<p>{escape(footer)}</p>"
    )
    return OutgoingEmail(
        to=admin.email,
        subject=f"Nueva comunidad pendiente: {community.name}",
        text=text,
        html=html,
    )

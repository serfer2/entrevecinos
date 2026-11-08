"""Avisos por correo de las solicitudes de acceso a una comunidad (HU-43)."""

from html import escape

from entrevecinos.application.communities.ports import MembershipRepository
from entrevecinos.application.mail.email_quota import EmailQuota
from entrevecinos.application.users.ports import OutgoingEmail
from entrevecinos.domain.communities.entities import Community
from entrevecinos.domain.mail.errors import EmailQuotaExceeded
from entrevecinos.domain.users.entities import User


class MembershipNotices:
    """Prepara los avisos y reserva una plaza del cupo por cada uno.

    Sin cupo no se prepara ninguno más: la solicitud o la aprobación se hacen igual, porque el
    aviso nunca debe impedirlas. `EmailQuota` ya registra el bloqueo.
    """

    def __init__(
        self, memberships: MembershipRepository, quota: EmailQuota, web_public_url: str
    ) -> None:
        self._memberships = memberships
        self._quota = quota
        self._web_public_url = web_public_url.rstrip("/")

    def request_received(self, community: Community, requester: User) -> list[OutgoingEmail]:
        """Un aviso por administrador aprobado de la comunidad, sin datos de contacto del vecino."""
        link = f"{self._web_public_url}/comunidades/{community.id}/gestion/solicitudes"
        messages: list[OutgoingEmail] = []
        for admin in self._memberships.list_admin_recipients(community.id):
            if admin.id == requester.id:
                continue
            if not self._reserve():
                break
            messages.append(_request_received(admin, requester, community, link))
        return messages

    def _reserve(self) -> bool:
        try:
            self._quota.reserve()
        except EmailQuotaExceeded:
            return False
        return True


def _request_received(
    admin: User, requester: User, community: Community, link: str
) -> OutgoingEmail:
    text = (
        f"Hola, {admin.full_name}:\n\n"
        f"{requester.full_name} ha pedido unirse a {community.name}.\n\n"
        f"Revisa la solicitud aquí:\n\n{link}\n\n"
        f"Recibes este correo porque administras {community.name} en EntreVecinos.\n"
    )
    html = (
        f"<p>Hola, {escape(admin.full_name)}:</p>"
        f"<p>{escape(requester.full_name)} ha pedido unirse a {escape(community.name)}.</p>"
        f'<p><a href="{escape(link)}">Revisar la solicitud</a></p>'
        f"<p>Recibes este correo porque administras {escape(community.name)} en EntreVecinos.</p>"
    )
    return OutgoingEmail(
        to=admin.email,
        subject=f"Nueva solicitud para unirse a {community.name}",
        text=text,
        html=html,
    )

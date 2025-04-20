import aiohttp

BASE_URL = "http://207.154.246.175:8099/api"
GET_USER_URL = f"{BASE_URL}/users/get/"
ADD_USER_URL = f"{BASE_URL}/users/add/"
UPDATE_USER_URL = f"{BASE_URL}/users/update/"
CREATE_INVITATION_URL = f"{BASE_URL}/users/invitations/create/"
INVITE_USER_URL = f"{BASE_URL}/users/invitations/invite/"


async def get_user(id: str | int) -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        return await session.get(f"{GET_USER_URL}{id}/")


async def add_user(data: dict) -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        return await session.post(ADD_USER_URL, json=data)


async def update_user(id: str | int, data: dict) -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        return await session.patch(f"{UPDATE_USER_URL}{id}/", json=data)


async def get_or_create_invitation(user_id: str | int) -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        return await session.get(f"{CREATE_INVITATION_URL}{user_id}/")


async def invite_user(user_id: str | int, invitation_token: str) -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        return await session.get(f"{INVITE_USER_URL}{invitation_token}/{user_id}/")


async def get_users() -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        return await session.get(GET_USER_URL)

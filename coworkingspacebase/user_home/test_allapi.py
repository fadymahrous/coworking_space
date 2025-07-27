import requests
import pytest

@pytest.fixture
def access_token_fulluser():
    data={'username':'fady','password':'xyz'}
    url='http://127.0.0.1:8000/api/token/'
    response=requests.post(url,data=data)
    response_json=response.json()
    return response_json['access']

@pytest.fixture
def access_token_emptyuser():
    data={'username':'reem','password':'xyz'}
    url='http://127.0.0.1:8000/api/token/'
    response=requests.post(url,data=data)
    response_json=response.json()
    return response_json['access']

def test_viewmenue(access_token_fulluser):
    headers={'Authorization':f'Bearer {access_token_fulluser}'}
    url='http://127.0.0.1:8000/v1/api/foodmenue/'
    response=requests.get(url,headers=headers)
    #Verify reponse Code
    assert response.status_code==200
    #Verify headers
    assert response.headers["Content-Type"] == "application/json"
    #Verfiy reponse data
    data_response=response.json()
    print(data_response)
    assert isinstance(data_response,dict)


def test_add_item_to_cart(access_token_fulluser):
    headers={'Authorization':f'Bearer {access_token_fulluser}'}
    data={'item_name':'Cappuccino Vanilla','count':'1'}
    url='http://127.0.0.1:8000/v1/api/cart/'
    response=requests.post(url,headers=headers,data=data)
    assert response.status_code==200
    headers={'Authorization':f'Bearer {access_token_fulluser}'}
    data={'item_name':'Hotdog','count':'5'}
    url='http://127.0.0.1:8000/v1/api/cart/'
    response=requests.post(url,headers=headers,data=data)
    assert response.status_code==200
    headers={'Authorization':f'Bearer {access_token_fulluser}'}
    data={'item_name':'Popcorn','count':'3'}
    url='http://127.0.0.1:8000/v1/api/cart/'
    response=requests.post(url,headers=headers,data=data)
    assert response.status_code==200

def test_viewcart_full(access_token_fulluser):
    headers={'Authorization':f'Bearer {access_token_fulluser}'}
    url='http://127.0.0.1:8000/v1/api/cart/'
    response=requests.get(url,headers=headers)
    #Verify reponse Code
    assert response.status_code==200
    #Verify headers
    assert response.headers["Content-Type"] == "application/json"
    #Verfiy reponse data
    data_response=response.json()
    print(data_response)
    assert isinstance(data_response,dict)
    assert 'item_name' in data_response['data'][0]
    assert 'count' in data_response['data'][0]

def test_viewcart_empty(access_token_emptyuser):
    headers={'Authorization':f'Bearer {access_token_emptyuser}'}
    url='http://127.0.0.1:8000/v1/api/cart/'
    response=requests.get(url,headers=headers)
    #Verify reponse Code
    assert response.status_code==404
    #Verify headers
    assert response.headers["Content-Type"] == "application/json"
    #Verfiy reponse data
    data_response=response.json()
    assert isinstance(data_response,dict)

def test_remove_item_from_cart(access_token_fulluser):
    headers={'Authorization':f'Bearer {access_token_fulluser}'}
    data={'item_name':'Hotdog'}
    url='http://127.0.0.1:8000/v1/api/cart/'
    response=requests.delete(url,headers=headers,data=data)
    assert response.status_code==200

def test_create_order(access_token_fulluser):
    headers={'Authorization':f'Bearer {access_token_fulluser}'}
    data={'table_number':3}
    url='http://127.0.0.1:8000/v1/api/order/'
    response=requests.post(url,headers=headers,data=data)
    assert response.status_code==200

def test_get_bill(access_token_fulluser):
    headers={'Authorization':f'Bearer {access_token_fulluser}'}
    url='http://127.0.0.1:8000/v1/api/bill/'
    response=requests.get(url,headers=headers)
    assert response.status_code==200

def test_submit_bill(access_token_fulluser):
    headers={'Authorization':f'Bearer {access_token_fulluser}'}
    url='http://127.0.0.1:8000/v1/api/bill/'
    response=requests.post(url,headers=headers)
    assert response.status_code==200
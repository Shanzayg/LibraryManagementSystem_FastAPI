from fastapi import FastAPI, Query
from typing import Optional, Literal

app = FastAPI()



@app.get("/",    tags=["General"],
    summary="Welcome to Library API",
    description="Welcome endpoint providing basic information about the Library Management API.")
def read_root():
    return {"hello!": "Welcome to the system !"}

@app.get('/health')
def get_health():
    return {'status': 'okay'}


#          ---- BOOKS DATABASE ----
books = {
    101: {
        "title": "Python Crash Course",
        "author": "Eric Matthes",
        "price": 1500,
        "genre": "Programming",
        "available": True
    },
    102: {
        "title": "Atomic Habits",
        "author": "James Clear",
        "price": 1200,
        "genre": "Self-help",
        "available": True
    },
    103: {
        "title": "Rich Dad Poor Dad",
        "author": "Robert Kiyosaki",
        "price": 1000,
        "genre": "Finance",
        "available": False
    },
    104: {
        "title": "The Alchemist",
        "author": "Paulo Coelho",
        "price": 900,
        "genre": "Fiction",
        "available": False
    },
    105: {
        "title": "Deep Work",
        "author": "Cal Newport",
        "price": 1300,
        "genre": "Productivity",
        "available": False
    }
}

#          ---- MEMBERS DATABASE ----
members ={
            101:{'name':'max' },
            102:{'name':'noor'},
            103:{'name':'asim'},
            104:{'name':'jane'},
            105:{'name':'lisbon'}
            }

#          ---- LOANS DATABASE ----
loans ={
            101:{'members_id':101, 'status':'borrowed' },
            102:{'members_id':102, 'status':'returned'},
            103:{'members_id':103, 'status':'borrowed'},
            104:{'members_id':104, 'status':'returned'},
            105:{'members_id':105, 'status':'returned'}
            }

#        ---- AUTHOR"S DATABASE ----
authors ={
            101:{'author':'Eric Mathes' },
            102:{'name':'James Clear'},
            103:{'name':'Robert Kiyosaki'},
            104:{'name':'Paulo Coelho'},
            105:{'name':'Cal Newport'}
            }

#  CREATE END GET POINTS AND RETREIVE INDIVIDUAL RECORDS ...
@app.get("/books/count" , tags=["Length"], summary='Counting the number of books', description="Counting the total number and the available and the unavailable number of books")
def count_books():
    available = sum(1 for b in books.values() if b["available"])
    return {
        "total_books": len(books),
        "available": available,
        "unavailable": len(books) - available,
    }

@app.get('/authors/{author_id}')
def get_author(author_id : int):
    if author_id in authors:
        return authors[author_id]
    
    return {'error ': "not found"}

@app.get("/books/{book_id}")
def get_books(book_id: int):
    if book_id in books:
        return books[book_id]
    
    return {'error':'not found'}

@app.get('/members/{members_id}')
def get_members(members_id : int):
    if members_id in members:
        return members[members_id]
    return {'error':'not found'}

@app.get('/loans/{loans_id}')
def get_loans(loans_id: int):
    if loans_id in loans:
        return loans[loans_id]
    return {'error':'not found'}

@app.get('/members/{members_id}/loans/{loans_id}')
def get_loans_status(members_id :int, loans_id: int):
    
    if members_id not in members:
        return {'error':'member not found'}
    
    if loans_id not in loans:
        return {'error': "loan does not exist"}

    loan = loans[loans_id]

    if loan['members_id'] != members_id:
        return {'this loan does not belong to this member.'}

    return loan


#  Search and filter: GET /books?title=python&author=smith&available=true
@app.get("/books")
def get_books(
    title: Optional[str] = None, # Optional query params using str | None = None

    author: Optional[str] = None,
    available: Optional[bool] = None,
    sort_by: Literal ['title','author','genre']='title' ,
    order: Literal['asc', 'desc'] = 'asc' ,
    skip: int = Query(0, ge=0), # Query params for listing: GET /books?skip=0&limit=10 (pagination)
    limit : int = Query(10, le=100, ge=0) 
):
    results = []
    for book_id, b in books.items():
        if title and title.lower() not in b["title"].lower():
            continue
        if author and author.lower() not in b["author"].lower():
            continue
        if available is not None and b["available"] != available:
            continue
        results.append({"id": book_id, **b})


#   Add sorting: GET /books?sort_by=title&order=desc
    def sort_key(b):
        value = b[sort_by]
        return value.lower() if isinstance(value, str) else value
    results.sort (key= sort_key, reverse= (order == 'desc'))

    return results [skip: skip+limit]

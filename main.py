
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Personal Expense Tracker")

# Allow requests from the frontend during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

expenses = {}
next_id = 1

class Expense(BaseModel):
    description: str
    amount: float = Field(gt=0)
    category: str

    @field_validator("description", "category")
    @classmethod
    def validate_text(cls, value):
        if not value.strip():
            raise ValueError("This field cannot be empty")
        return value.strip()

@app.get("/")
async def home():
    return FileResponse("index.html")

@app.post("/expenses", status_code=201)
async def add_expense(expense: Expense):
    global next_id

    new_expense = {
        "id": next_id,
        **expense.model_dump()
    }

    expenses[next_id] = new_expense
    next_id += 1

    return {
        "message": "Expense added successfully",
        "expense": new_expense
    }

@app.get("/expenses")
async def get_expenses():
    return list(expenses.values())

@app.put("/expenses/{expense_id}")
async def update_expense(expense_id: int, expense: Expense):
    if expense_id not in expenses:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    expenses[expense_id] = {
        "id": expense_id,
        **expense.model_dump()
    }

    return {
        "message": "Expense updated successfully",
        "expense": expenses[expense_id]
    }

@app.delete("/expenses/{expense_id}")
async def delete_expense(expense_id: int):
    if expense_id not in expenses:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    del expenses[expense_id]

    return {"message": "Expense deleted successfully"}
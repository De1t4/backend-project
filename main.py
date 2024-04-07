from fastapi import FastAPI, UploadFile, HTTPException,File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cloudinary
import cloudinary.uploader 
from cloudinary import api
import os
from dotenv import load_dotenv
from peewee import MySQLDatabase
from peewee import Model, CharField, PrimaryKeyField

app = FastAPI()
load_dotenv()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cloudinary.config( 
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


db = MySQLDatabase(
  os.getenv("DB_DATABASE"),
  user=os.getenv("DB_USER"), 
  password=os.getenv("DB_PASSWORD"), 
  host=os.getenv("DB_HOST")
)

class BaseModel(Model):
  class Meta:
    database = db

class product(BaseModel):
  idProduct = PrimaryKeyField()
  ProductURL = CharField(max_length=255)

# db.connect()
# fetchData = product.select()
# for data in fetchData:
# 	print(data.idProduct, data.ProductURL)
# db.close()


# Ejecutar consulta para crear una tabla


@app.post('/upload')
async def upload_file(file: UploadFile = File(...)):
	if not file:
		raise HTTPException(status_code=404, detail="File not found")
	try:
		db.connect()
		response = cloudinary.uploader.upload(file.file, folder="uploads")

		responseURL = response['secure_url']
		
		newURL = product(ProductURL=responseURL)
		newURL.save()

		return JSONResponse(content={"detail": "File received successfully", "url":response['secure_url']}, status_code=200)
	except Exception as error:
		return HTTPException(status_code=500, detail=f"error en el servidor {error}")
	finally:
		db.close()


@app.get('/images')
async def getImage():
	try:
		db.connect()
		fetchData = product.select()
		dataURL = []
		for data in fetchData:
			objectURL = {
				"idProduct": data.idProduct,
				"URL":data.ProductURL
			}
			dataURL.append(objectURL)

		return dataURL

	except Exception as error:
			return HTTPException({"error": error})
	finally:
		db.close()
	

@app.post('/saludar')
async def helloUser():
		return JSONResponse({"hola":"usuario"})

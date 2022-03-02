import os
from flask import Flask, request, render_template
import cv2
import numpy as np
import imutils
import easyocr
import ibm_db
app = Flask(__name__, static_url_path='')

# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

@app.route('/', methods =["GET", "POST"])

@app.route('/', methods =["GET", "POST"])
def extractVehicleNumber():
    if request.method == "POST":
       # getting input with name = fname in HTML form
       image = request.form.get("img")
       img = cv2.imread(image)
       gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
       bfilter = cv2.bilateralFilter(gray, 11, 17, 17) #Noise reduction
       edged = cv2.Canny(bfilter, 30, 200) #Edge detection
       keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
       contours = imutils.grab_contours(keypoints)
       contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
       location = None
       for contour in contours:
        	approx = cv2.approxPolyDP(contour, 10, True)
       		if len(approx) == 4:
         	    location = approx
         	    break
       mask = np.zeros(gray.shape, np.uint8)
       new_image = cv2.drawContours(mask, [location], 0,255, -1)
       new_image = cv2.bitwise_and(img, img, mask=mask)
       (x,y) = np.where(mask==255)
       (x1, y1) = (np.min(x), np.min(y))
       (x2, y2) = (np.max(x), np.max(y))
       cropped_image = gray[x1:x2+1, y1:y2+1]
       reader =  easyocr.Reader(['en'])
       text = reader.recognize(cropped_image)
       number = text[0][1]
       return number         
    return render_template("validate.html")



#This is as background process triggers at predefined interval and get the data from Vehicle track table and interact with AI Vehicle Number extractor for getting vehicle number
# and it uses various Document validation  methods validate the vehicle violations , if any violations detected it will alert the phone number for the location, and also update Violation Data table. If we #can’t send sms then I will provide a method for UI , so that UI can keep calling that method to# #get details
def violatioDector():
    conn_string = “DATABASE=bludb;HOSTNAME=ea286ace-86c7-4d5b-8580-3fbfa46b1c66.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31505;PROTOCOL=TCPIP;UID=lls36792;PWD=tCMJ0Z7UZFPthb7Y;SECURITY=SSL”
    try:
     db2con = ibm_db.connect(conn_string,“”,“”)
     if db2con:
        print(“Connection ...... [SUCCESS]“)
        ibm_db.close(db2con)
     else:
      print(“Connection ...... [FAILURE]“)
    except Exception as e:
        print(e)
        print(“err”)
    #getimages from CCTV
    #Findoutthe location
    #validate the documents
    #validate violation
    #validate ID presence in other locations
    #update the table if ant violation found


    
#This method get the  details from Alerter table for the given location
def getAlertDetails(area,db2conn):
    alertDet =['000000']
    if db2con:     
        selectQuery = "select * from aleter where area = "+ area
        stmt = ibm_db.exec_immediate(db2con, selectQuery)
        dictionary = ibm_db.fetch_assoc(stmt)
       
        while dictionary != False:
            number= dictionary["NUMBER"]
            arrea = dictionary["AREA"]
            alertDet.append(number)
            dictionary = ibm_db.fetch_assoc(stmt)
    
    return alertDet
#This method get the violation details from RTOViolation table for the given vehicle number from the DB
def getViolationDetials (ID,db2conn):
    violationDet =['000000']
    if db2con:     
        selectQuery = "select * from RTOViolation where ID = "+ ID
        stmt = ibm_db.exec_immediate(db2con, selectQuery)
        dictionary = ibm_db.fetch_assoc(stmt)
       
        while dictionary != False:
            viotype= dictionary["TYPE"]
            violationDet.append(viotype)
            dictionary = ibm_db.fetch_assoc(stmt)
    
    return violationDet
#: This method get the document details from VachileDetails table for the given vehicle number from the DB
def getVechileDocuments (ID,db2conn):
    violationDet =['000000']
    if db2con:     
        selectQuery = "select * from VachileDetails where ID = "+ ID
        stmt = ibm_db.exec_immediate(db2con, selectQuery)
        dictionary = ibm_db.fetch_assoc(stmt)
       
        while dictionary != False:
            doctype= dictionary["TYPE"]
            violationDet.append(doctype)
            dictionary = ibm_db.fetch_assoc(stmt)
    
    return violationDet

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True);

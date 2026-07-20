"""
Trekky — Master Database Seeder
=================================
Run this once on a fresh database (after `python app.py` has created the
DB file and the three core accounts) to populate the full realistic dataset:

    100 Trekkers  |  40 Staff  |  80 real-world Treks (spread across 2026)
    ~800+ Bookings with slot tracking  |  ~250 Reviews on completed treks

Usage:
    python seed_database.py
"""

import random
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash
import app
import models

# Reference date — used to assign trek statuses correctly
TODAY = date(2026, 7, 21)

# ─────────────────────────────────────────────────────────────────────────────
# REAL-WORLD PEOPLE DATA
# ─────────────────────────────────────────────────────────────────────────────

TREKKER_DATA = [
    # (full_name, email, dob_str, contact)
    ("Arjun Sharma",         "arjun.sharma91@gmail.com",      "1991-04-15", "+91 9812345670"),
    ("Priya Mehta",          "priya.mehta88@gmail.com",       "1988-09-22", "+91 9823456781"),
    ("Rohan Verma",          "rohan.verma95@gmail.com",       "1995-11-03", "+91 9834567892"),
    ("Sneha Patel",          "sneha.patel92@yahoo.com",       "1992-06-18", "+91 9845678903"),
    ("Vikram Nair",          "vikram.nair87@gmail.com",       "1987-02-27", "+91 9856789014"),
    ("Anjali Singh",         "anjali.singh94@gmail.com",      "1994-08-11", "+91 9867890125"),
    ("Karan Gupta",          "karan.gupta89@hotmail.com",     "1989-12-05", "+91 9878901236"),
    ("Meera Iyer",           "meera.iyer96@gmail.com",        "1996-03-30", "+91 9889012347"),
    ("Sahil Joshi",          "sahil.joshi93@gmail.com",       "1993-07-14", "+91 9890123458"),
    ("Divya Reddy",          "divya.reddy90@gmail.com",       "1990-01-09", "+91 9801234569"),
    ("Amit Kulkarni",        "amit.kulkarni85@gmail.com",     "1985-05-23", "+91 9712345670"),
    ("Pooja Bhatt",          "pooja.bhatt97@gmail.com",       "1997-10-16", "+91 9723456781"),
    ("Nikhil Desai",         "nikhil.desai91@gmail.com",      "1991-08-08", "+91 9734567892"),
    ("Ritu Agarwal",         "ritu.agarwal93@yahoo.com",      "1993-02-19", "+91 9745678903"),
    ("Saurabh Tiwari",       "saurabh.tiwari86@gmail.com",    "1986-11-28", "+91 9756789014"),
    ("Kavitha Krishnan",     "kavitha.krishnan94@gmail.com",  "1994-04-07", "+91 9767890125"),
    ("Manish Kapoor",        "manish.kapoor88@gmail.com",     "1988-07-20", "+91 9778901236"),
    ("Sonali Bose",          "sonali.bose96@gmail.com",       "1996-01-13", "+91 9789012347"),
    ("Deepak Pandey",        "deepak.pandey90@hotmail.com",   "1990-09-04", "+91 9790123458"),
    ("Asha Menon",           "asha.menon83@gmail.com",        "1983-06-25", "+91 9801234560"),
    ("Rahul Saxena",         "rahul.saxena92@gmail.com",      "1992-12-17", "+91 9612345671"),
    ("Swati Pillai",         "swati.pillai89@gmail.com",      "1989-03-11", "+91 9623456782"),
    ("Tarun Malhotra",       "tarun.malhotra95@gmail.com",    "1995-10-29", "+91 9634567893"),
    ("Ishaan Chatterjee",    "ishaan.chatt97@gmail.com",      "1997-05-06", "+91 9645678904"),
    ("Nidhi Choudhary",      "nidhi.choudh91@gmail.com",      "1991-08-21", "+91 9656789015"),
    ("Gaurav Sharma",        "gaurav.sharma84@yahoo.com",     "1984-01-15", "+91 9667890126"),
    ("Lakshmi Rajan",        "lakshmi.rajan93@gmail.com",     "1993-11-10", "+91 9678901237"),
    ("Pranav Doshi",         "pranav.doshi90@gmail.com",      "1990-06-03", "+91 9689012348"),
    ("Shweta Ghosh",         "shweta.ghosh87@gmail.com",      "1987-04-27", "+91 9690123459"),
    ("Aditya Bansal",        "aditya.bansal98@gmail.com",     "1998-09-14", "+91 9601234560"),
    ("Rekha Nambiar",        "rekha.nambiar85@gmail.com",     "1985-07-08", "+91 9512345672"),
    ("Suresh Kumar",         "suresh.kumar92@gmail.com",      "1992-02-22", "+91 9523456783"),
    ("Archana Srivastava",   "archana.sriv88@yahoo.com",      "1988-12-01", "+91 9534567894"),
    ("Vishal Bajaj",         "vishal.bajaj94@gmail.com",      "1994-05-19", "+91 9545678905"),
    ("Radhika Pillai",       "radhika.pillai91@gmail.com",    "1991-10-07", "+91 9556789016"),
    ("Ajay Mishra",          "ajay.mishra86@gmail.com",       "1986-03-24", "+91 9567890127"),
    ("Pallavi Garg",         "pallavi.garg96@gmail.com",      "1996-08-12", "+91 9578901238"),
    ("Kunal Thakkar",        "kunal.thakkar89@hotmail.com",   "1989-01-28", "+91 9589012349"),
    ("Namita Jain",          "namita.jain93@gmail.com",       "1993-06-16", "+91 9590123450"),
    ("Harish Rao",           "harish.rao80@gmail.com",        "1980-11-04", "+91 9501234561"),
    ("Usha Nair",            "usha.nair88@gmail.com",         "1988-04-09", "+91 9412345673"),
    ("Mohit Sehgal",         "mohit.sehgal95@gmail.com",      "1995-09-23", "+91 9423456784"),
    ("Geeta Bhattacharya",   "geeta.bhatt90@gmail.com",       "1990-02-14", "+91 9434567895"),
    ("Sunil Patil",          "sunil.patil87@yahoo.com",       "1987-07-31", "+91 9445678906"),
    ("Rashmi Acharya",       "rashmi.acharya93@gmail.com",    "1993-12-20", "+91 9456789017"),
    ("Naveen Dixit",         "naveen.dixit91@gmail.com",      "1991-05-08", "+91 9467890128"),
    ("Bhavna Chawla",        "bhavna.chawla84@gmail.com",     "1984-10-26", "+91 9478901239"),
    ("Rohit Aggarwal",       "rohit.aggarwal97@gmail.com",    "1997-03-13", "+91 9489012340"),
    ("Preeti Menon",         "preeti.menon92@gmail.com",      "1992-08-01", "+91 9490123451"),
    ("Sanjay Dubey",         "sanjay.dubey85@gmail.com",      "1985-01-17", "+91 9401234562"),
    ("Tanvi Kulkarni",       "tanvi.kulkarni96@gmail.com",    "1996-06-05", "+91 9312345674"),
    ("Mayank Sinha",         "mayank.sinha89@gmail.com",      "1989-11-22", "+91 9323456785"),
    ("Jyoti Chopra",         "jyoti.chopra94@hotmail.com",    "1994-04-10", "+91 9334567896"),
    ("Aamir Khan",           "aamir.khan91@gmail.com",        "1991-09-28", "+91 9345678907"),
    ("Shilpa Yadav",         "shilpa.yadav87@gmail.com",      "1987-02-16", "+91 9356789018"),
    ("Abhishek Tripathi",    "abhishek.trip93@gmail.com",     "1993-07-04", "+91 9367890129"),
    ("Riya Fernandes",       "riya.fernandes98@gmail.com",    "1998-12-21", "+91 9378901230"),
    ("Chirag Patel",         "chirag.patel90@gmail.com",      "1990-05-09", "+91 9389012341"),
    ("Lavanya Iyer",         "lavanya.iyer86@gmail.com",      "1986-10-27", "+91 9390123452"),
    ("Varun Bhatia",         "varun.bhatia95@gmail.com",      "1995-03-14", "+91 9301234563"),
    ("Poonam Sharma",        "poonam.sharma88@gmail.com",     "1988-08-02", "+91 9212345675"),
    ("Hitesh Chand",         "hitesh.chand92@yahoo.com",      "1992-01-19", "+91 9223456786"),
    ("Mamta Gupta",          "mamta.gupta84@gmail.com",       "1984-06-07", "+91 9234567897"),
    ("Sandeep Rawat",        "sandeep.rawat97@gmail.com",     "1997-11-24", "+91 9245678908"),
    ("Kritika Joshi",        "kritika.joshi91@gmail.com",     "1991-04-12", "+91 9256789019"),
    ("Vivek Sharma",         "vivek.sharma85@gmail.com",      "1985-09-30", "+91 9267890120"),
    ("Deepika Nair",         "deepika.nair94@gmail.com",      "1994-02-17", "+91 9278901231"),
    ("Rajan Krishnaswamy",   "rajan.krish89@gmail.com",       "1989-07-05", "+91 9289012342"),
    ("Sunita Misra",         "sunita.misra93@hotmail.com",    "1993-12-23", "+91 9290123453"),
    ("Harshit Agrawala",     "harshit.agr96@gmail.com",       "1996-05-11", "+91 9201234564"),
    ("Vandana Tewari",       "vandana.tewari82@gmail.com",    "1982-10-29", "+91 9112345676"),
    ("Akash Pandya",         "akash.pandya90@gmail.com",      "1990-03-17", "+91 9123456787"),
    ("Hemant Mahajan",       "hemant.mahajan87@gmail.com",    "1987-08-04", "+91 9134567898"),
    ("Nandini Kaur",         "nandini.kaur95@gmail.com",      "1995-01-21", "+91 9145678909"),
    ("Rajesh Bhardwaj",      "rajesh.bhard92@yahoo.com",      "1992-06-09", "+91 9156789010"),
    ("Shruti Deshpande",     "shruti.desh88@gmail.com",       "1988-11-27", "+91 9167890121"),
    ("Alok Mittal",          "alok.mittal94@gmail.com",       "1994-04-15", "+91 9178901232"),
    ("Chandni Verma",        "chandni.verma91@gmail.com",     "1991-09-02", "+91 9189012343"),
    ("Jagdish Ramaiah",      "jagdish.ram80@gmail.com",       "1980-02-20", "+91 9190123454"),
    ("Tara Bhatt",           "tara.bhatt96@gmail.com",        "1996-07-08", "+91 9101234565"),
    ("Manav Sethi",          "manav.sethi89@gmail.com",       "1989-12-26", "+91 9012345677"),
    ("Shobha Chetty",        "shobha.chetty93@gmail.com",     "1993-05-14", "+91 9023456788"),
    ("Vikas Malhotra",       "vikas.malh86@gmail.com",        "1986-10-01", "+91 9034567899"),
    ("Ananya Iyer",          "ananya.iyer97@gmail.com",       "1997-03-19", "+91 9045678900"),
    ("Kapil Tomar",          "kapil.tomar91@gmail.com",       "1991-08-06", "+91 9056789011"),
    ("Leena Rajput",         "leena.rajput84@hotmail.com",    "1984-01-24", "+91 9067890122"),
    ("Siddharth Menon",      "siddharth.men95@gmail.com",     "1995-06-12", "+91 9078901233"),
    ("Nisha Goel",           "nisha.goel90@gmail.com",        "1990-11-29", "+91 9089012344"),
    ("Ritesh Pandey",        "ritesh.pandey87@gmail.com",     "1987-04-17", "+91 9090123455"),
    ("Aparna Kumar",         "aparna.kumar93@gmail.com",      "1993-09-04", "+91 9001234566"),
    ("Darshan Pillai",       "darshan.pillai98@gmail.com",    "1998-02-22", "+91 8912345677"),
    ("Gargi Mukherjee",      "gargi.mukh85@gmail.com",        "1985-07-10", "+91 8923456788"),
    ("Tarun Bose",           "tarun.bose92@gmail.com",        "1992-12-28", "+91 8934567899"),
    ("Ira Shukla",           "ira.shukla94@gmail.com",        "1994-05-15", "+91 8945678900"),
    ("Sumit Lal",            "sumit.lal88@yahoo.com",         "1988-10-03", "+91 8956789011"),
    ("Vandana Pillai",       "vandana.pillai96@gmail.com",    "1996-03-21", "+91 8967890122"),
    ("Kiran Bajaj",          "kiran.bajaj91@gmail.com",       "1991-08-08", "+91 8978901233"),
    ("Meenal Desai",         "meenal.desai89@gmail.com",      "1989-01-26", "+91 8989012344"),
    ("Ajit Narayanan",       "ajit.nara83@gmail.com",         "1983-06-14", "+91 8990123455"),
    ("Roshni Varma",         "roshni.varma95@gmail.com",      "1995-11-01", "+91 8901234566"),
]

STAFF_DATA = [
    # (full_name, email, dob_str, contact)
    ("Rajiv Mehta",          "rajiv.mehta@trekky.in",          "1982-03-14", "+91 8800112233"),
    ("Sunita Sharma",        "sunita.sharma@trekky.in",        "1985-07-22", "+91 8811223344"),
    ("Vikrant Singh",        "vikrant.singh@trekky.in",        "1980-11-09", "+91 8822334455"),
    ("Pooja Nair",           "pooja.nair@trekky.in",           "1989-05-18", "+91 8833445566"),
    ("Amit Rawat",           "amit.rawat@trekky.in",           "1978-09-02", "+91 8844556677"),
    ("Kavitha Rajan",        "kavitha.rajan@trekky.in",        "1991-01-27", "+91 8855667788"),
    ("Deepak Jha",           "deepak.jha@trekky.in",           "1984-06-13", "+91 8866778899"),
    ("Reshma Pillai",        "reshma.pillai@trekky.in",        "1987-10-05", "+91 8877889900"),
    ("Suresh Thapa",         "suresh.thapa@trekky.in",         "1979-02-21", "+91 8888990011"),
    ("Anita Bhat",           "anita.bhat@trekky.in",           "1983-08-16", "+91 8899001122"),
    ("Manoj Ghosh",          "manoj.ghosh@trekky.in",          "1976-12-04", "+91 8700112233"),
    ("Leela Krishnan",       "leela.krishnan@trekky.in",       "1990-04-29", "+91 8711223344"),
    ("Sanjeev Kapoor",       "sanjeev.kapoor@trekky.in",       "1981-09-17", "+91 8722334455"),
    ("Ritu Pandey",          "ritu.pandey@trekky.in",          "1988-02-03", "+91 8733445566"),
    ("Arun Yadav",           "arun.yadav@trekky.in",           "1977-07-12", "+91 8744556677"),
    ("Seema Malhotra",       "seema.malhotra@trekky.in",       "1986-11-28", "+91 8755667788"),
    ("Nitin Desai",          "nitin.desai@trekky.in",          "1982-04-15", "+91 8766778899"),
    ("Harpreet Kaur",        "harpreet.kaur@trekky.in",        "1990-08-01", "+91 8777889900"),
    ("Ramesh Patil",         "ramesh.patil@trekky.in",         "1975-01-19", "+91 8788990011"),
    ("Divya Shetty",         "divya.shetty@trekky.in",         "1984-06-07", "+91 8799001122"),
    ("Kiran Chandra",        "kiran.chandra@trekky.in",        "1987-10-24", "+91 8600112233"),
    ("Meenakshi Ramu",       "meenakshi.ramu@trekky.in",       "1980-03-11", "+91 8611223344"),
    ("Pradeep Tiwari",       "pradeep.tiwari@trekky.in",       "1978-08-29", "+91 8622334455"),
    ("Shanti Iyer",          "shanti.iyer@trekky.in",          "1985-01-16", "+91 8633445566"),
    ("Bhushan Gupta",        "bhushan.gupta@trekky.in",        "1983-06-04", "+91 8644556677"),
    ("Archana Rao",          "archana.rao@trekky.in",          "1988-10-21", "+91 8655667788"),
    ("Tushar Vaidya",        "tushar.vaidya@trekky.in",        "1976-04-08", "+91 8666778899"),
    ("Radha Gowda",          "radha.gowda@trekky.in",          "1991-09-26", "+91 8677889900"),
    ("Mohan Tripathi",       "mohan.tripathi@trekky.in",       "1979-02-13", "+91 8688990011"),
    ("Gauri Sawant",         "gauri.sawant@trekky.in",         "1986-07-01", "+91 8699001122"),
    ("Prakash Menon",        "prakash.menon@trekky.in",        "1974-11-18", "+91 8500112233"),
    ("Usha Dubey",           "usha.dubey@trekky.in",           "1989-04-06", "+91 8511223344"),
    ("Chetan Shah",          "chetan.shah@trekky.in",          "1982-09-23", "+91 8522334455"),
    ("Savita Kulkarni",      "savita.kulkarni@trekky.in",      "1985-02-10", "+91 8533445566"),
    ("Rahul Bhatt",          "rahul.bhatt@trekky.in",          "1977-07-28", "+91 8544556677"),
    ("Lalitha Subramaniam",  "lalitha.subra@trekky.in",        "1983-12-15", "+91 8555667788"),
    ("Ajay Kumar Sharma",    "ajayk.sharma@trekky.in",         "1980-05-03", "+91 8566778899"),
    ("Veena Nambiar",        "veena.nambiar@trekky.in",        "1987-09-20", "+91 8577889900"),
    ("Dinesh Bose",          "dinesh.bose@trekky.in",          "1975-02-07", "+91 8588990011"),
    ("Saraswathi Pillai",    "saraswathi.pillai@trekky.in",    "1984-07-25", "+91 8599001122"),
]

# ─────────────────────────────────────────────────────────────────────────────
# TREK CATALOGUE — 80 real-world treks spread across all of 2026
# Format: (name, location, difficulty, total_slots, duration_days, start_date, image)
# ─────────────────────────────────────────────────────────────────────────────

TREK_CATALOGUE = [
    # Jan – Feb  (Himalayan winter snowtreks)
    ("Kedarkantha Summit Trek",        "Uttarkashi, Uttarakhand, India",        "Moderate", 12, 6,  date(2026,1,5),   "treks/ebc.png"),
    ("Brahmatal Trek",                 "Chamoli, Uttarakhand, India",           "Moderate", 10, 6,  date(2026,1,12),  "treks/ebc.png"),
    ("Dayara Bugyal Winter Trek",      "Uttarkashi, Uttarakhand, India",        "Easy",     14, 5,  date(2026,1,18),  "treks/mont-blanc.png"),
    ("Pangarchulla Peak Expedition",   "Chamoli, Uttarakhand, India",           "Hard",     8,  8,  date(2026,1,25),  "treks/ebc.png"),
    ("Chopta Tungnath Chandrashila",   "Rudraprayag, Uttarakhand, India",       "Moderate", 12, 5,  date(2026,2,2),   "treks/mont-blanc.png"),
    ("Nag Tibba Trek",                 "Mussoorie, Uttarakhand, India",         "Easy",     16, 3,  date(2026,2,8),   "treks/zion.png"),
    ("Valley of Flowers Winter Trek",  "Chamoli, Uttarakhand, India",           "Moderate", 10, 7,  date(2026,2,15),  "treks/mont-blanc.png"),
    ("Ali Bedni Bugyal Trek",          "Chamoli, Uttarakhand, India",           "Moderate", 12, 7,  date(2026,2,22),  "treks/ebc.png"),
    # Mar – Apr  (Spring Himalayan classics)
    ("Roopkund Skeleton Lake Trek",    "Chamoli, Uttarakhand, India",           "Hard",     8,  8,  date(2026,3,2),   "treks/ebc.png"),
    ("Har Ki Dun Valley Trek",         "Uttarkashi, Uttarakhand, India",        "Moderate", 12, 7,  date(2026,3,8),   "treks/mont-blanc.png"),
    ("Kuari Pass Trek",                "Chamoli, Uttarakhand, India",           "Moderate", 14, 7,  date(2026,3,15),  "treks/ebc.png"),
    ("Sandakphu Phalut Trek",          "Darjeeling, West Bengal, India",        "Moderate", 12, 7,  date(2026,3,20),  "treks/mont-blanc.png"),
    ("Pindari Glacier Trek",           "Bageshwar, Uttarakhand, India",         "Moderate", 10, 9,  date(2026,3,28),  "treks/ebc.png"),
    ("Annapurna Base Camp Trek",       "Kaski, Gandaki, Nepal",                 "Moderate", 10, 11, date(2026,4,3),   "treks/ebc.png"),
    ("Everest Base Camp Trek",         "Khumbu, Solukhumbu, Nepal",             "Hard",     8,  14, date(2026,4,5),   "treks/ebc.png"),
    ("Poon Hill Trek",                 "Myagdi, Gandaki, Nepal",                "Easy",     16, 4,  date(2026,4,10),  "treks/mont-blanc.png"),
    ("Manaslu Circuit Trek",           "Gorkha, Gandaki, Nepal",                "Hard",     6,  14, date(2026,4,12),  "treks/ebc.png"),
    ("Tour du Mont Blanc",             "Chamonix-Mont-Blanc, France",           "Moderate", 10, 11, date(2026,4,18),  "treks/mont-blanc.png"),
    ("Triund Trek",                    "Dharamshala, Himachal Pradesh, India",  "Easy",     20, 2,  date(2026,4,24),  "treks/zion.png"),
    ("Hampta Pass Trek",               "Manali, Himachal Pradesh, India",       "Moderate", 14, 5,  date(2026,4,28),  "treks/mont-blanc.png"),
    # May – Jun  (Pre-monsoon high-altitude)
    ("Stok Kangri Expedition",         "Leh-Ladakh, Jammu & Kashmir, India",    "Hard",     6,  9,  date(2026,5,4),   "treks/ebc.png"),
    ("Markha Valley Trek",             "Leh-Ladakh, Jammu & Kashmir, India",    "Moderate", 10, 8,  date(2026,5,8),   "treks/mont-blanc.png"),
    ("Kashmir Great Lakes Trek",       "Sonamarg, Jammu & Kashmir, India",      "Hard",     8,  7,  date(2026,5,15),  "treks/ebc.png"),
    ("Beas Kund Trek",                 "Manali, Himachal Pradesh, India",       "Moderate", 14, 4,  date(2026,5,20),  "treks/mont-blanc.png"),
    ("Sar Pass Trek",                  "Kasol, Himachal Pradesh, India",        "Moderate", 12, 5,  date(2026,5,25),  "treks/mont-blanc.png"),
    ("Rupin Pass Trek",                "Uttarkashi, Uttarakhand, India",        "Hard",     8,  8,  date(2026,5,28),  "treks/ebc.png"),
    ("Deo Tibba Base Camp Trek",       "Manali, Himachal Pradesh, India",       "Moderate", 10, 6,  date(2026,6,2),   "treks/mont-blanc.png"),
    ("Spiti Valley Trek",              "Spiti, Himachal Pradesh, India",        "Hard",     8,  8,  date(2026,6,6),   "treks/ebc.png"),
    ("Pin Bhaba Pass Trek",            "Kinnaur-Spiti, Himachal Pradesh",       "Hard",     6,  9,  date(2026,6,12),  "treks/ebc.png"),
    ("Kheerganga Trek",                "Parvati Valley, Himachal Pradesh",      "Easy",     20, 2,  date(2026,6,18),  "treks/zion.png"),
    ("Nagalapuram Waterfalls Trek",    "Tiruvallur, Tamil Nadu, India",         "Easy",     18, 1,  date(2026,6,21),  "treks/zion.png"),
    # Jul  (Monsoon — Western Ghats & Sahyadri)
    ("Kumara Parvatha Trek",           "Coorg, Karnataka, India",               "Hard",     12, 2,  date(2026,7,4),   "treks/ebc.png"),
    ("Tadiandamol Peak Trek",          "Coorg, Karnataka, India",               "Moderate", 14, 2,  date(2026,7,5),   "treks/mont-blanc.png"),
    ("Kodachadri Trek",                "Shimoga, Karnataka, India",             "Moderate", 14, 2,  date(2026,7,10),  "treks/mont-blanc.png"),
    ("Rajmachi Fort Trek",             "Raigad, Maharashtra, India",            "Easy",     20, 1,  date(2026,7,12),  "treks/zion.png"),
    ("Harishchandragad Trek",          "Ahmednagar, Maharashtra, India",        "Hard",     10, 2,  date(2026,7,16),  "treks/ebc.png"),
    ("Kalavantin Durg Trek",           "Raigad, Maharashtra, India",            "Hard",     12, 1,  date(2026,7,18),  "treks/ebc.png"),
    ("Bhrigu Lake Trek",               "Manali, Himachal Pradesh, India",       "Moderate", 12, 5,  date(2026,7,24),  "treks/mont-blanc.png"),
    ("Friendship Peak Expedition",     "Manali, Himachal Pradesh, India",       "Hard",     6,  7,  date(2026,7,28),  "treks/ebc.png"),
    # Aug – Sep  (Post-monsoon Himalayan routes reopen)
    ("Kalsubai Peak Trek",             "Ahmednagar, Maharashtra, India",        "Moderate", 14, 1,  date(2026,8,3),   "treks/mont-blanc.png"),
    ("Lohagad Fort Trek",              "Pune, Maharashtra, India",              "Easy",     20, 1,  date(2026,8,9),   "treks/zion.png"),
    ("Valley of Flowers Trek",         "Chamoli, Uttarakhand, India",           "Moderate", 12, 6,  date(2026,8,1),   "treks/mont-blanc.png"),
    ("Kedarnath Trek",                 "Rudraprayag, Uttarakhand, India",       "Moderate", 16, 3,  date(2026,8,5),   "treks/ebc.png"),
    ("Gomukh Tapovan Trek",            "Uttarkashi, Uttarakhand, India",        "Hard",     8,  7,  date(2026,8,10),  "treks/ebc.png"),
    ("Gangotri to Gomukh Trek",        "Uttarkashi, Uttarakhand, India",        "Moderate", 12, 3,  date(2026,8,15),  "treks/mont-blanc.png"),
    ("Roopkund Lake Trek",             "Chamoli, Uttarakhand, India",           "Hard",     8,  8,  date(2026,8,18),  "treks/ebc.png"),
    ("Satopanth Lake Trek",            "Chamoli, Uttarakhand, India",           "Hard",     6,  10, date(2026,8,22),  "treks/ebc.png"),
    ("Kuari Pass Autumn Trek",         "Chamoli, Uttarakhand, India",           "Moderate", 14, 7,  date(2026,8,28),  "treks/mont-blanc.png"),
    ("Milam Glacier Trek",             "Pithoragarh, Uttarakhand, India",       "Moderate", 10, 9,  date(2026,9,4),   "treks/mont-blanc.png"),
    ("Pindari to Sunderdhunga Trek",   "Bageshwar, Uttarakhand, India",         "Hard",     8,  11, date(2026,9,8),   "treks/ebc.png"),
    ("Dzongri Trek",                   "North Sikkim, Sikkim, India",           "Moderate", 10, 7,  date(2026,9,12),  "treks/mont-blanc.png"),
    ("Goecha La Trek",                 "West Sikkim, Sikkim, India",            "Hard",     8,  11, date(2026,9,15),  "treks/ebc.png"),
    ("Green Lake Trek",                "North Sikkim, Sikkim, India",           "Hard",     6,  12, date(2026,9,20),  "treks/ebc.png"),
    ("Sandakphu Trek",                 "Darjeeling, West Bengal, India",        "Moderate", 12, 6,  date(2026,9,25),  "treks/mont-blanc.png"),
    ("Sinhagad Fort Trek",             "Pune, Maharashtra, India",              "Easy",     22, 1,  date(2026,9,1),   "treks/zion.png"),
    ("Visapur Fort Trek",              "Pune, Maharashtra, India",              "Moderate", 16, 1,  date(2026,9,5),   "treks/mont-blanc.png"),
    ("Kugti Pass Trek",                "Chamba, Himachal Pradesh, India",       "Hard",     6,  9,  date(2026,9,28),  "treks/ebc.png"),
    # Oct – Nov  (Golden season — Himalayan classics)
    ("Annapurna Circuit Trek",         "Gandaki Province, Nepal",               "Hard",     8,  14, date(2026,10,2),  "treks/ebc.png"),
    ("Langtang Valley Trek",           "Rasuwa, Bagmati, Nepal",                "Moderate", 10, 8,  date(2026,10,5),  "treks/mont-blanc.png"),
    ("Gokyo Lakes Trek",               "Solukhumbu, Koshi, Nepal",              "Hard",     8,  12, date(2026,10,8),  "treks/ebc.png"),
    ("Three Passes Trek Nepal",        "Solukhumbu, Koshi, Nepal",              "Hard",     6,  18, date(2026,10,10), "treks/ebc.png"),
    ("Hampta Pass to Chandratal",      "Kullu-Lahaul, Himachal Pradesh",        "Hard",     10, 6,  date(2026,10,15), "treks/ebc.png"),
    ("Bali Pass Trek",                 "Uttarkashi, Uttarakhand, India",        "Hard",     8,  8,  date(2026,10,18), "treks/ebc.png"),
    ("Kalindikhal Pass Trek",          "Uttarkashi, Uttarakhand, India",        "Hard",     6,  10, date(2026,10,22), "treks/ebc.png"),
    ("Kedartal Trek",                  "Uttarkashi, Uttarakhand, India",        "Hard",     8,  6,  date(2026,10,26), "treks/ebc.png"),
    ("Tungnath Chandrashila Trek",     "Rudraprayag, Uttarakhand, India",       "Moderate", 14, 4,  date(2026,10,30), "treks/mont-blanc.png"),
    ("Dayara Bugyal Autumn Trek",      "Uttarkashi, Uttarakhand, India",        "Easy",     16, 4,  date(2026,11,2),  "treks/mont-blanc.png"),
    ("Dodital Trek",                   "Uttarkashi, Uttarakhand, India",        "Moderate", 14, 5,  date(2026,11,6),  "treks/mont-blanc.png"),
    ("Deoria Tal Chandrashila Trek",   "Rudraprayag, Uttarakhand, India",       "Easy",     16, 4,  date(2026,11,10), "treks/zion.png"),
    ("Kumari Glacier Trek",            "Pithoragarh, Uttarakhand, India",       "Hard",     6,  7,  date(2026,11,14), "treks/ebc.png"),
    ("Kheerganga Kalgha Trek",         "Kullu, Himachal Pradesh, India",        "Moderate", 12, 4,  date(2026,11,18), "treks/mont-blanc.png"),
    ("Tarsar Marsar Lake Trek",        "Pahalgam, Jammu & Kashmir, India",      "Moderate", 10, 6,  date(2026,11,22), "treks/mont-blanc.png"),
    ("Coorg Peak Challenge",           "Madikeri, Karnataka, India",            "Moderate", 14, 2,  date(2026,11,26), "treks/mont-blanc.png"),
    ("Velliangiri Hills Trek",         "Coimbatore, Tamil Nadu, India",         "Hard",     10, 1,  date(2026,11,29), "treks/ebc.png"),
    # Dec  (Winter Himalayan treks)
    ("Kedarkantha December Edition",   "Uttarkashi, Uttarakhand, India",        "Moderate", 12, 6,  date(2026,12,3),  "treks/ebc.png"),
    ("Brahmatal Winter Trek",          "Chamoli, Uttarakhand, India",           "Moderate", 10, 6,  date(2026,12,8),  "treks/ebc.png"),
    ("Nag Tibba Winter Trek",          "Mussoorie, Uttarakhand, India",         "Easy",     16, 3,  date(2026,12,13), "treks/zion.png"),
    ("Chopta Winter Snowtrek",         "Rudraprayag, Uttarakhand, India",       "Moderate", 12, 4,  date(2026,12,18), "treks/mont-blanc.png"),
    ("Deoban Trek",                    "Chakrata, Uttarakhand, India",          "Easy",     18, 3,  date(2026,12,22), "treks/zion.png"),
    ("Har Ki Dun Winter Edition",      "Uttarkashi, Uttarakhand, India",        "Moderate", 10, 7,  date(2026,12,26), "treks/mont-blanc.png"),
]

# ─────────────────────────────────────────────────────────────────────────────
# REVIEW TEXT POOL
# ─────────────────────────────────────────────────────────────────────────────

REVIEWS_BY_RATING = {
    5: [
        "Absolutely life-changing experience. The Himalayan sunrise from the summit was worth every ounce of effort. Trekky's team was phenomenal!",
        "The trail was perfectly curated — scenic campsites, expertly acclimatised itinerary and a guide who clearly loved every kilometre of it. 10/10.",
        "We started as strangers in the group and ended as lifelong friends. The trek itself was breathtaking but the community Trekky creates is the real magic.",
        "Every single detail was organised flawlessly — from the porters to the safety briefings to the warm dal bhat at camp. Couldn't have asked for more.",
        "Reached the summit after three days of honest effort. Standing there with the clouds below us was surreal. Thank you Trekky for making it possible.",
        "One of the most rewarding physical experiences of my life. Pristine wilderness, no mobile signal, just mountains and silence. Pure bliss.",
        "The assigned guide was extremely knowledgeable about local flora, alpine safety and altitude management. I felt completely safe throughout.",
        "Already planning my next Trekky expedition. The quality of meals, gear check and team spirit was several notches above what I expected.",
        "Absolutely life-changing. The summit views were beyond words and the Trekky team was exceptional throughout.",
        "Perfect trail, perfect team. Every detail was handled with care. Already planning my next trip with Trekky!",
        "One of the most rewarding experiences of my life. Pristine wilderness, expert guidance and great group energy.",
    ],
    4: [
        "Great overall experience — the trail was well-marked and the group was well-paced. Lost half a star only because Day 3 campsite was a bit cramped.",
        "Really enjoyed the trek. The guide was excellent and the views were spectacular. The bag-load porters made the journey so much more comfortable.",
        "Solid, well-organised adventure. The final ascent was tougher than I expected for 'Moderate' difficulty, but I made it and felt incredibly proud.",
        "Beautiful landscapes and a competent team. Logistics were smooth. The only hiccup was a delayed meal on Day 2 due to weather.",
        "A thoroughly enjoyable multi-day trek. Recommend bringing an extra pair of gloves — the ridge gets genuinely cold even in summer.",
        "Very good experience overall. The trek felt authentic and not overcrowded. Pre-departure briefing was thorough and professional.",
        "Happy with the quality of trekking equipment provided. The route through the pine forests on Day 1 was my personal highlight.",
        "Professionally managed with good safety protocols. The altitude gain profile was sensible and I did not face any acclimatisation issues.",
        "Great trek overall. The route was well-organised and the guide was knowledgeable. Minor logistics issue on Day 2 but resolved quickly.",
        "Really enjoyed the experience. Challenging but manageable. The campsite views made every uphill worth it.",
        "Well-paced, safe and scenic. Would recommend to any intermediate trekker.",
    ],
    3: [
        "Decent trek but felt slightly over-hyped. The views at the top were good but the trail was muddy and poorly maintained on the final stretch.",
        "Average experience. The guide was helpful but communication on the start time was confusing. Still glad I came — the landscape was beautiful.",
        "Middle-of-the-road expedition. Nothing went badly wrong but nothing was exceptional either. The campfire on Day 2 evening was the highlight.",
        "The trek itself is lovely but logistics around pickup and drop were disorganised. Internal team coordination needs improvement.",
        "Good route selection but the group was too large for a comfortable pace. Felt rushed at some campsites. Views were genuinely stunning though.",
        "Good experience but a few rough edges — the campsite on Day 1 was crowded and meals were delayed. The trek itself is beautiful though.",
        "Decent trek. Nothing exceptional stood out but nothing went wrong either. The final ridge section had great views.",
    ],
    2: [
        "Disappointed with the experience. The guide seemed inexperienced on the higher section of the trail and safety protocols felt thin.",
        "Trail condition was much worse than described. Several sections were dangerously slippery and no prior warning was given to participants.",
        "Felt under-supported at high altitude. The meals were sparse and the sleeping bags were not adequate for the night temperature.",
        "Below expectations. Logistics were disorganised and the guide seemed unfamiliar with the route on Day 3.",
    ],
    1: [
        "Would not recommend. Equipment was substandard and the guide abandoned the group for an hour on a difficult section. Very unsafe.",
        "Extremely poor organisation. Several bookings were double-confirmed and the group was simply too large for the trail.",
        "Very poor experience. Safety measures were inadequate and communication from the team was almost non-existent.",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def determine_trek_status(start_date: date, end_date: date, slots_left: int) -> str:
    """Assign a realistic status based on today's date and available slots."""
    if TODAY > end_date:
        return "Completed"
    elif TODAY >= start_date:
        return "Ongoing"
    else:
        days_until = (start_date - TODAY).days
        if days_until > 60:
            return random.choice(["Upcoming", "Draft", "Booking Open"])
        elif days_until > 14:
            return "Closed" if slots_left == 0 else random.choice(["Booking Open", "Upcoming"])
        else:
            return "Closed" if slots_left == 0 else "Booking Open"


# ─────────────────────────────────────────────────────────────────────────────
# MAIN SEED FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def seed_everything():
    with app.app.app_context():
        hashed_pw = generate_password_hash("password123")
        existing_emails     = {u.user_email        for u in models.User.query.all()}
        existing_display_ids = {u.user_display_id  for u in models.User.query.all()}

        # ── STEP 1: Create 100 Trekkers ──────────────────────────────────
        print("Creating trekkers...")
        for name, email, dob_str, contact in TREKKER_DATA:
            if email in existing_emails:
                continue
            dob = date.fromisoformat(dob_str)
            while True:
                did = f"U{random.randint(1, 999):03d}"
                if did not in existing_display_ids:
                    existing_display_ids.add(did)
                    break
            models.db.session.add(models.User(
                user_display_id=did, user_email=email, user_password_hash=hashed_pw,
                user_role="trekker", user_full_name=name, user_dob=dob, user_contact_no=contact,
            ))
            existing_emails.add(email)
        models.db.session.commit()
        trekker_users = models.User.query.filter_by(user_role="trekker").all()
        print(f"  Trekkers in DB: {len(trekker_users)}")

        # ── STEP 2: Create 40 Staff ───────────────────────────────────────
        print("Creating staff...")
        for name, email, dob_str, contact in STAFF_DATA:
            if email in existing_emails:
                continue
            dob = date.fromisoformat(dob_str)
            while True:
                did = f"S{random.randint(1, 999):03d}"
                if did not in existing_display_ids:
                    existing_display_ids.add(did)
                    break
            u = models.User(
                user_display_id=did, user_email=email, user_password_hash=hashed_pw,
                user_role="staff", user_full_name=name, user_dob=dob, user_contact_no=contact,
            )
            models.db.session.add(u)
            models.db.session.flush()   # get u.user_id before committing
            models.db.session.add(models.Staff(
                user_id=u.user_id, staff_name=name,
                staff_contact_details=contact, staff_status="Approved",
            ))
            existing_emails.add(email)
        models.db.session.commit()
        all_staff = models.Staff.query.filter_by(staff_status="Approved").all()
        print(f"  Approved staff in DB: {len(all_staff)}")

        # ── STEP 3: Create 80 Treks ───────────────────────────────────────
        print("Creating treks...")
        existing_trek_ids   = {t.trek_display_id for t in models.Trek.query.all()}
        existing_trek_names = {t.trek_name       for t in models.Trek.query.all()}

        for tname, tloc, tdiff, tslots, tdur, tstart, timg in TREK_CATALOGUE:
            if tname in existing_trek_names:
                continue
            tend = tstart + timedelta(days=tdur)
            assigned_sid = random.choice(all_staff).staff_id if all_staff and random.random() > 0.3 else None
            while True:
                tid = f"T{random.randint(1, 999):03d}"
                if tid not in existing_trek_ids:
                    existing_trek_ids.add(tid)
                    break
            status = determine_trek_status(tstart, tend, tslots)
            models.db.session.add(models.Trek(
                trek_display_id=tid, trek_name=tname, trek_location=tloc,
                trek_difficulty=tdiff, trek_duration=tdur,
                trek_available_slots=tslots, trek_status=status,
                trek_start_date=tstart, trek_end_date=tend,
                trek_image_filename=timg, assigned_staff_id=assigned_sid,
            ))
            existing_trek_names.add(tname)
        models.db.session.commit()
        all_treks = models.Trek.query.all()
        print(f"  Treks in DB: {len(all_treks)}")

        # ── STEP 4: Simulate Bookings ─────────────────────────────────────
        print("Simulating bookings...")

        # Build family/friend clusters (groups of 1-4 who book together)
        shuffled_trekkers = list(trekker_users)
        random.shuffle(shuffled_trekkers)
        clusters, i = [], 0
        while i < len(shuffled_trekkers):
            size = random.randint(1, 4)
            clusters.append(shuffled_trekkers[i:i+size])
            i += size

        booking_status_by_trek = {
            "Completed":    ["Completed", "Completed", "Completed", "Trek Abandoned", "Cancelled"],
            "Ongoing":      ["Booked",    "Booked",    "Trek Abandoned"],
            "Booking Open": ["Booked",    "Booked",    "Cancelled"],
            "Closed":       ["Booked",    "Cancelled", "Refunded"],
            "Upcoming":     ["Booked"],
            "Draft":        [],
            "Cancelled":    ["Cancelled", "Refunded"],
        }
        eligible_treks = [t for t in all_treks if t.trek_status not in ("Draft", "Cancelled")]
        # Load ALL existing booking pairs from DB so re-runs skip already-created bookings
        existing_booking_pairs       = {(b.user_id, b.trek_id) for b in models.Booking.query.all()}
        existing_booking_display_ids = {b.booking_display_id   for b in models.Booking.query.all()}
        slots_remaining = {t.trek_id: t.trek_available_slots for t in all_treks}

        if existing_booking_pairs:
            print(f"  Skipping already-seeded booking pairs: {len(existing_booking_pairs)} found in DB")

        def gen_bid():
            while True:
                bid = f"B{random.randint(1, 999):03d}"
                if bid not in existing_booking_display_ids:
                    existing_booking_display_ids.add(bid)
                    return bid

        total_bookings = 0
        for cluster in clusters:
            chosen = random.sample(eligible_treks, min(random.randint(2, 6), len(eligible_treks)))
            for trek in chosen:
                valid = booking_status_by_trek.get(trek.trek_status, [])
                if not valid:
                    continue
                for trekker in cluster:
                    pair = (trekker.user_id, trek.trek_id)
                    if pair in existing_booking_pairs:
                        continue
                    b_status = random.choice(valid)
                    if b_status == "Booked" and slots_remaining[trek.trek_id] <= 0:
                        b_status = "Cancelled"
                    if b_status == "Booked":
                        slots_remaining[trek.trek_id] -= 1
                    latest   = min(trek.trek_start_date, TODAY)
                    earliest = trek.trek_start_date - timedelta(days=60)
                    if earliest > latest:
                        earliest = latest - timedelta(days=5)
                    days_r = max(1, (latest - earliest).days)
                    b_date = datetime.combine(
                        earliest + timedelta(days=random.randint(0, days_r)),
                        datetime.min.time()
                    )
                    models.db.session.add(models.Booking(
                        booking_display_id=gen_bid(),
                        user_id=trekker.user_id,
                        trek_id=trek.trek_id,
                        booking_status=b_status,
                        booking_date=b_date,
                    ))
                    existing_booking_pairs.add(pair)
                    total_bookings += 1
                    if total_bookings % 200 == 0:
                        models.db.session.commit()
        models.db.session.commit()
        print(f"  Bookings created: {total_bookings}")

        # ── STEP 5: Recalculate slots & finalise trek statuses ────────────
        print("Finalising trek statuses and slot counts...")
        for trek in models.Trek.query.all():
            active = models.Booking.query.filter(
                models.Booking.trek_id == trek.trek_id,
                models.Booking.booking_status.in_(["Booked", "Completed"]),
            ).count()
            trek.trek_available_slots = max(0, trek.trek_available_slots - active)
            trek.trek_status = determine_trek_status(
                trek.trek_start_date, trek.trek_end_date, trek.trek_available_slots
            )
            if trek.trek_status == "Completed":
                models.Booking.query.filter_by(
                    trek_id=trek.trek_id, booking_status="Booked"
                ).update({"booking_status": "Completed"})
            elif trek.trek_status in ("Draft", "Cancelled"):
                models.Booking.query.filter_by(
                    trek_id=trek.trek_id, booking_status="Booked"
                ).update({"booking_status": "Refunded"})
        models.db.session.commit()

        # ── STEP 6: Reviews for completed treks ───────────────────────────
        print("Adding reviews for completed treks...")
        existing_review_pairs = {(r.user_id, r.trek_id) for r in models.Review.query.all()}
        existing_review_ids   = {r.review_display_id for r in models.Review.query.all() if r.review_display_id}

        def gen_rid():
            while True:
                rid = f"R{random.randint(1, 999):03d}"
                if rid not in existing_review_ids:
                    existing_review_ids.add(rid)
                    return rid

        total_reviews = 0
        for trek in models.Trek.query.filter_by(trek_status="Completed").all():
            for booking in models.Booking.query.filter_by(
                trek_id=trek.trek_id, booking_status="Completed"
            ).all():
                if (booking.user_id, trek.trek_id) in existing_review_pairs:
                    continue
                if random.random() > 0.78:   # ~78% of completers leave a review
                    continue
                rating = random.choices([5, 4, 3, 2, 1], weights=[40, 35, 15, 7, 3])[0]
                text   = random.choice(REVIEWS_BY_RATING[rating])
                r_date = datetime.combine(
                    trek.trek_end_date + timedelta(days=random.randint(1, 20)),
                    datetime.min.time()
                )
                models.db.session.add(models.Review(
                    review_display_id=gen_rid(),
                    user_id=booking.user_id,
                    trek_id=trek.trek_id,
                    rating=rating,
                    review_text=text,
                    created_at=r_date,
                ))
                existing_review_pairs.add((booking.user_id, trek.trek_id))
                total_reviews += 1
                if total_reviews % 100 == 0:
                    models.db.session.commit()
        models.db.session.commit()
        print(f"  Reviews created: {total_reviews}")

        # ── FINAL SUMMARY ─────────────────────────────────────────────────
        print("\n=== SEED COMPLETE ===")
        print(f"Total Users:    {models.User.query.count()}")
        print(f"  Admins:       {models.User.query.filter_by(user_role='admin').count()}")
        print(f"  Staff:        {models.User.query.filter_by(user_role='staff').count()}")
        print(f"  Trekkers:     {models.User.query.filter_by(user_role='trekker').count()}")
        print(f"Approved Staff: {models.Staff.query.filter_by(staff_status='Approved').count()}")
        print(f"Total Treks:    {models.Trek.query.count()}")
        for s in ["Draft", "Upcoming", "Booking Open", "Closed", "Ongoing", "Completed", "Cancelled"]:
            print(f"  {s:15s}: {models.Trek.query.filter_by(trek_status=s).count()}")
        print(f"Total Bookings: {models.Booking.query.count()}")
        for s in ["Booked", "Completed", "Cancelled", "Refunded", "Trek Abandoned"]:
            print(f"  {s:15s}: {models.Booking.query.filter_by(booking_status=s).count()}")
        print(f"Total Reviews:  {models.Review.query.count()}")


if __name__ == "__main__":
    seed_everything()

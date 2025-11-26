########################################################### IMPORT MODULE
import sys
from pathlib import Path
from io import BytesIO
from functools import partial
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import (QPropertyAnimation, QPoint, QObject, QEvent, Qt, QTimer)
from PyQt5.QtGui import (QFont, QFontDatabase, QColor, QIcon, QImage, QPixmap, QPainter, QBrush)
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QMessageBox, QLabel, QFrame, QVBoxLayout
import sqlite3
from app.assets import res_rc
from app.utils.BarGraph import create_bar_chart_widget
from app.database.database import Database, database
from app.utils.util import (add_chart_to_dashboard, display_scholarships_admin, display_scholarships_util, MyWindow,
                            HoverShadow, load_font, DesignShadow, get_rounded_stretched_pixmap)
from app.utils.DonutChart import create_donut_chart_widget
from app.utils.BarGraph2 import create_bar_chart_widget2
from app.utils.util2 import (display_accepted_scholarships_admin, display_rejected_scholarships_admin, display_dropped_scholarships_admin)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, username=None, app_manager=None):
        super().__init__()

        # Basic props
        self.username = username or "hrvycstddcll"
        self.app_manager = app_manager

        # UI & resources
        self.setup_paths_and_icons()
        self.setup_ui()

        # Styling / behavior
        self.setup_fonts()
        self.setup_shadows()
        self.navigations()

        # Load user info & initial data
        self.setup_user_info()
        database.refresh_scholar_data()
        self._refresh_dashboard_chart()
        self.setup_connections()

    ########################################################### Path & UI
    def setup_paths_and_icons(self):
        """Ensure referenced asset files exist and expose as attributes"""
        current_file_path = Path(__file__).resolve()
        self.project_root = current_file_path.parent.parent
        asset_paths = {
            'ui': self.project_root / 'assets' / 'MainWindow.ui',
            'isb_font': self.project_root / 'assets' / 'InclusiveSans-Bold.ttf',
            'isr_font': self.project_root / 'assets' / 'InclusiveSans-Regular.ttf',
            'profilelabel': self.project_root / 'assets' / 'profilephoto.png'
        }
        for key, path in asset_paths.items():
            if not path.exists():
                raise FileNotFoundError(f"Required file not found: {path}")
            setattr(self, f"{key}_path", path)

    ########################################################### Setup UIs
    def setup_ui(self):
        uic.loadUi(self.ui_path, self)
        self.sidebar.setHidden(True)
        self.nextbtn_2.setDisabled(True)
        self.information.setDisabled(True)
        self.appform.setDisabled(True)
        self.finish.setDisabled(True)

        ########################################################### Set up if Admin
        if database.is_Admin(self.username):
            display_scholarships_admin(self.scholarscrolls, database)
            self.cpy.setHidden(True)
            self.scholar.setVisible(True)
            self.scholar2.setVisible(True)
            self.applybtn.clicked.connect(lambda: QMessageBox.information(self, "Admin", "You're an admin — you don't apply for scholarships."))
            self.applybtn2.clicked.connect(lambda: QMessageBox.information(self, "Admin", "You're an admin — you don't apply for scholarships."))
            self.applybtn5.clicked.connect(lambda: QMessageBox.information(self, "Admin", "You're an admin — you don't apply for scholarships."))
            self.refreshbtn.clicked.connect(lambda : (self.setup_user_info(), self._refresh_dashboard_chart()))

        else:
            self.scholar.setVisible(False)
            self.scholar2.setVisible(False)
            self.cpy.setVisible(True)
            # Connect scholarship entry handlers (these only connect once)
            self.applybtn.clicked.connect(self.handleBSU)
            self.applybtn2.clicked.connect(self.handleBCD)
            self.applybtn5.clicked.connect(self.handleDSWD)
            self.update_scholar_status()
            self.refreshbtn.clicked.connect(self.update_scholar_status)

    ########################################################### Styling
    def setup_fonts(self):
        """Register and set fonts on widgets (keeps your original mapping)"""
        self.largelabel_font = load_font(self.isb_font_path, 36, bold=True)
        self.medlar_font = load_font(self.isb_font_path, 20, bold=True)
        self.mediumlabel_font = load_font(self.isb_font_path, 14, bold=True)
        self.small_font = load_font(self.isb_font_path, 12, bold=True)
        self.field_font = load_font(self.isr_font_path, 10, bold=False)

        font_map = {
            self.largelabel_font: [],
            self.medlar_font: [self.bsutext],
            self.mediumlabel_font: [
                self.applybtn, self.applybtn2, self.applybtn3, self.applybtn4, self.applybtn5, self.applybtn6,
                self.financialLabel, self.bcdLabel, self.educLabel, self.lll_2, self.acad_2, self.dost_2,
                self.about2, self.dashboard2, self.scholar2, self.exit2, self.profile2, self.home2, self.bsutext2,
                self.TP, self.nextbtn, self.nextbtn_2, self.nextbtn_3, self.bsusubmit, self.reminder
            ],
            self.small_font: [self.bsuconfirm],
            self.field_font: [
                self.financialLabel2, self.financialLabel3, self.bcdLabel2, self.bcdLabel3, self.educLabel2,
                self.educLabel3, self.lll2, self.lll3, self.acad2, self.acad3, self.dost2, self.dost3,
                self.bsutext3, self.bsutext3_2, self.terms, self.cpy, self.useremail, self.label_32
            ],
        }
        for font, widgets in font_map.items():
            for widget in widgets:
                widget.setFont(font)

    def setup_shadows(self):
        """Apply reusable shadow styling (keeps your design calls)"""
        widgets_to_shadow = [
            self.financial_assistance, self.bcd_scholarship, self.lll, self.acad, self.educ_assistance, self.dost
        ]
        for widget in widgets_to_shadow:
            DesignShadow(widget, 25, offset=(0, 15), color=QColor(0, 0, 0, 180))
        DesignShadow(self.homewid, 50, offset=(0, 0), color=QColor(0, 0, 0, 255))
        dash = [self.totAcc, self.totNon, self.dashboard1, self.dashboardBar, self.dashboardBar3,
                self.label_17, self.label_10]
        for widget in dash:
            DesignShadow(widget, 20, offset=(0, 0), color=QColor(0, 0, 0, 180))

    ########################################################### Navigations
    def navigations(self):
        """Connect navigation signals. These connections are done once during setup."""
        self.home.clicked.connect(lambda: self.stacks.setCurrentIndex(1))
        self.home2.clicked.connect(lambda: self.stacks.setCurrentIndex(1))
        self.profile.clicked.connect(lambda: self.stacks.setCurrentIndex(0))
        self.profile2.clicked.connect(lambda: self.stacks.setCurrentIndex(0))
        self.stacks.currentChanged.connect(self._on_tab_changed)
        self.dashboard.clicked.connect(lambda: self.stacks.setCurrentIndex(2))
        self.dashboard2.clicked.connect(lambda: self.stacks.setCurrentIndex(2))
        self.scholar.clicked.connect(lambda: self.stacks.setCurrentIndex(3))
        self.scholar2.clicked.connect(lambda: self.stacks.setCurrentIndex(3))
        self.about.clicked.connect(lambda: self.stacks.setCurrentIndex(5))
        self.about2.clicked.connect(lambda: self.stacks.setCurrentIndex(5))
        self.accepted.clicked.connect(lambda: display_accepted_scholarships_admin(self.AdminArea, database))
        self.accepted.click()
        self.rejected.clicked.connect(lambda: display_rejected_scholarships_admin(self.AdminArea, database))
        self.dropped.clicked.connect(lambda: display_dropped_scholarships_admin(self.AdminArea, database))

        # scholarship stack navigation
        self.nextbtn_2.setDisabled(True)
        self.terms_and_policy.clicked.connect(lambda: self.bsustacks.setCurrentIndex(1))
        self.nextbtn.clicked.connect(lambda: self.bsustacks.setCurrentIndex(1))
        self.information.clicked.connect(lambda: self.bsustacks.setCurrentIndex(2))
        self.nextbtn_2.clicked.connect(lambda: self.bsustacks.setCurrentIndex(2))
        self.appform.clicked.connect(lambda: self.bsustacks.setCurrentIndex(3))
        self.nextbtn_3.clicked.connect(lambda: self.bsustacks.setCurrentIndex(3))

        # Connect the main scholarship filters
        self.SNone.toggled.connect(self.interactive_dashboard)
        self.SBCD.toggled.connect(self.interactive_dashboard)
        self.SBSU.toggled.connect(self.interactive_dashboard)
        self.SDSWD.toggled.connect(self.interactive_dashboard)

        # Connect the college filters (All must point to the update method)
        self.SCICS.toggled.connect(self.interactive_dashboard)
        self.SCTE.toggled.connect(self.interactive_dashboard)
        self.SCHS.toggled.connect(self.interactive_dashboard)
        self.SCAS.toggled.connect(self.interactive_dashboard)
        self.SCAB.toggled.connect(self.interactive_dashboard)
        self.SCCJE.toggled.connect(self.interactive_dashboard)

    def setup_connections(self):
        try:
            self.editbtn.clicked.connect(self.open_update_profile)
        except AttributeError:
            print("Warning: 'editProfileButton' not found in MainWindow UI. Profile edit functionality not connected.")

    def open_update_profile(self):
        if self.app_manager and self.username:
            self.app_manager.show_update_window(username=self.username)
        else:
            QMessageBox.warning(
                self,
                "Profile Editor Error",
                "Cannot open the profile editor because the current user session or application context is incomplete. Please try logging in again."
            )

    ########################################################### Handle Scholarships
    def handleBSU(self):
        """Setup BSU scholarship UI and safe connect buttons for this scholarship."""
        self.reset_scholarship_form()
        self._setup_bsu_scholarship()
        self.set_up_scholarship_buttons(scholarship_name="BSU FINANCIAL ASSISTANCE")
        self.stacks.setCurrentIndex(4)
        self.bsustacks.setCurrentIndex(0)

    def handleBCD(self):
        self.reset_scholarship_form()
        self._setup_bcd_scholarship()
        self.set_up_scholarship_buttons(scholarship_name="BCD SCHOLARSHIP")
        self.stacks.setCurrentIndex(4)
        self.bsustacks.setCurrentIndex(0)

    def handleDSWD(self):
        self.reset_scholarship_form()
        self._setup_dswd_scholarship()
        self.set_up_scholarship_buttons(scholarship_name="DSWD EDUCATIONAL ASSISTANCE")
        self.stacks.setCurrentIndex(4)
        self.bsustacks.setCurrentIndex(0)

    def _setup_dswd_scholarship(self):
        # Set images
        self.label_11.setPixmap(QPixmap(":/images/educ.png"))
        self.label_3.setPixmap(QPixmap(":/images/educ.png"))

        # Set scholarship name and header
        self.bsutext.setText("DSWD EDUCATIONAL ASSISTANCE")
        self.label_12.setText("DEPARTMENT OF SOCIAL WELFARE AND DEVELOPMENT")
        self.label_13.setText("Supporting Students in Need")

        # Description
        dswd_text = (
            "The DSWD Scholarship provides financial assistance to students from marginalized "
            "and vulnerable communities. It aims to support education access and continuity "
            "for those who require social welfare aid. Scholars receive financial support each "
            "academic year until they finish their degree."
        )
        self.bsutext3.setText(dswd_text)

        # Privacy & data terms
        privacy_terms = (
            "By submitting this application, you consent to DSWD collecting, processing, and storing "
            "your personal information strictly for evaluating and administering this scholarship. "
            "DSWD ensures confidentiality and legal protection of your personal data."
        )
        self.bsutext3_2.setText(privacy_terms)

        # Consent statement
        consent_statement = (
            "I hereby agree to the collection, processing, storage, and use of my personal information "
            "by DSWD for scholarship purposes, and I understand my rights under applicable privacy laws."
        )
        self.terms.setText(consent_statement)

        # Application rules
        application_rules = (
            "• Read all guidelines before filling the form.\n"
            "• Complete all fields accurately; do not leave blanks."
        )
        self.label_55.setText(application_rules)

        # Submission rules
        submission_rules = (
            "• Only complete applications will be considered.\n"
            "• Updates on application status will be provided after evaluation."
        )
        self.label_32.setText(submission_rules)

    def _setup_bcd_scholarship(self):
        self.label_11.setPixmap(QPixmap(":/images/bcd.png"))
        self.label_3.setPixmap(QPixmap(":/images/altlogo.png"))
        self.bsutext.setText("BCD SCHOLARSHIP")
        self.label_12.setText("BIO CLICK DONE SCHOLARSHIP")
        self.label_13.setText("Empowering Your Future")

        bcdtext = (
            "The BCD SCHOLARSHIP offers direct financial aid to college students who excel academically, "
            "display strong leadership qualities, and actively engage in community service. This program "
            "guarantees a fixed monetary grant each academic year, ensuring consistent support to eligible "
            "scholars until they earn their bachelor's degree."
        )
        self.bsutext3.setText(bcdtext)

        privacy_terms = (
            "By completing and submitting this scholarship application form, you grant your full and explicit "
            "consent to the BCD SCHOLARSHIP administration to collect, process, and use your personal information "
            "solely for the purpose of evaluating and administering your scholarship application.\n\n"
            "In full adherence to the principles of data privacy and confidentiality, the BCD SCHOLARSHIP program "
            "is committed to protecting the personal data you provide from misuse, unauthorized access, disclosure, "
            "alteration, or destruction..."
        )
        self.bsutext3_2.setText(privacy_terms)

        consent_statement = (
            "I hereby: (1) agree to the collection, use, storage, and processing of my personal information, "
            "as well as the retention and subsequent disposal or destruction thereof, in accordance with the above "
            "terms and conditions; (2) warrant that my personal information was provided voluntarily by me to the BCD "
            "SCHOLARSHIP program; ..."
        )
        self.terms.setText(consent_statement)

        application_rules = (
            "• Please read the BCD SCHOLARSHIP Guidelines and Requirements thoroughly before accomplishing this application form.\n\n"
            "• Fill out this application form completely, accurately, and legibly. Ensure all required fields are addressed."
        )
        self.label_55.setText(application_rules)

        submission_rules = (
            "• Only applications that have submitted all complete documentary requirements will be processed.\n\n"
            "• The BCD SCHOLARSHIP administration will provide an update on your application status after the official closing date."
        )
        self.label_32.setText(submission_rules)

    def _setup_bsu_scholarship(self):
        self.label_11.setPixmap(QPixmap(":/images/bsutrans.png"))
        self.label_3.setPixmap(QPixmap(":/images/bsutrans.png"))
        self.bsutext.setText("BATANGAS STATE UNIVERSITY FINANCIAL ASSISTANCE")
        self.label_12.setText("BATANGAS STATE UNIVERSITY FINANCIAL ASSISTANCE")
        self.label_13.setText("The National Engineering University")
        bcdtext = (
            "The Batangas State University financial assistance supports outstanding college students "
            "who possess good academic record, demonstrate leadership potential and community involvement, "
            "and require financial assistance to pursue higher education."
        )
        self.bsutext3.setText(bcdtext)

        privacy_terms = (
            """By accomplishing this scholarship application form and providing personal information, you are granting full consent to Batangas State University Financial Assistance to collect and use your personal information for the evaluation of your scholarship application.
        In compliance with Republic Act No. 10173, otherwise known as the Data Privacy Act of 2012, BSU shall take reasonable steps to protect any personal data you provide from misuse and unauthorized access, disclosure, alteration, or destruction. BSU has taken reasonable steps to safeguard your personal information by restricting who may access the same and by installing physical and electronic security systems.
        BSU will store your information for as long as the purpose for collecting the same exists or is required by law, regulation, or its policies. Your personal information will be retained in compliance with applicable legal or regulatory requirements and archived as historical data of BSU. Your personal information shall be disposed of or destroyed as soon as BSU no longer needs the same in processing your application.
        You may request for a copy of your personal information to be given in paper or electronic form, provided that BSU is given reasonable time to extract and reproduce the same in accordance with the circumstances surrounding the request. In case of any errors, you may request to have corrections or removal made, which shall be processed by BSU unless there are legal, practical, or contractual reasons preventing the same."""
        )
        self.bsutext3_2.setText(privacy_terms)

        consent_statement = (
            """I hereby: (1) agree to the collection, use, storage, and processing of my personal information, and also to the retention and thereafter the disposal or destruction thereof in accordance with the above terms and conditions; (2) warrant that my personal information was provided voluntarily by me to BSU; (3) acknowledge and agree that it may be processed and made accessible to Batangas State University; and (4) agree to hold BSU, its directors, officers, employees, and agents free and harmless from any and all losses, liabilities, and/or claims of any nature which it may suffer or incur from or in connection with its reliance on this consent."""
        )
        self.terms.setText(consent_statement)

        application_rules = (
            "• Please read the BatstateU College Scholarship Guidelines and requirements before accomplishing the form.\n\n"
            "• Fill out this application form properly and completely."
        )
        self.label_55.setText(application_rules)

        submission_rules = (
            "• Only those who have submitted complete documentary requirements will be entertained.\n"
            "• BSU will provide a status of your application after the closing of submission."
        )
        self.label_32.setText(submission_rules)

    def safe_disconnect(self, button):
        try:
            button.clicked.disconnect()
        except (TypeError, RuntimeError):
            pass
        except Exception:
            pass

    ########################################################### Buttons
    def set_up_scholarship_buttons(self, scholarship_name):
        for btn in (self.bsuconfirm, self.finish, self.bsusubmit):
            self.safe_disconnect(btn)

        self.bsuconfirm.clicked.connect(partial(self._on_confirm_click, scholarship_name))
        self.finish.clicked.connect(self.scholarshipsubmit)
        self.bsusubmit.clicked.connect(self.scholarshipsubmit)

        if self.user_info:
            profile_blob = self.user_info[5]
            if profile_blob:
                img = QImage.fromData(profile_blob)
                pixmap = QPixmap.fromImage(img)
                self.bsuprofile.setPixmap(pixmap)

            self.bsufirst.setText(self.user_info[6] or "")
            self.bsulast.setText(self.user_info[7] or "")
            self.bsumi.setText(self.user_info[8] or "")
            self.bsusuffix.setText(self.user_info[9] or "")
            self.bsusex.setText(self.user_info[11] or "")
            self.bsucivilstat.setText(self.user_info[10] or "")
            self.bsuno.setText(self.user_info[19] or "")
            self.bsumunicipality.setText(self.user_info[18] or "")
            self.bsuemail.setText(self.user_info[3] or "")
            self.bsucourse.setText(self.user_info[15] or "")
            self.bsuprogram.setText(self.user_info[17] or "")
            self.bsuyl.setText(self.user_info[16] or "")

    def _on_confirm_click(self, scholarship_name):
        self.bsuconfirm.setEnabled(False)
        try:
            self.confirmsubmit(scholarship_name=scholarship_name, status="PENDING", gwa_text=self.bsugwa.text().strip())
        finally:
            QTimer.singleShot(300, lambda: self.bsuconfirm.setEnabled(True))

    ########################################################### Validation
    def scholarshipsubmit(self):
        required_fields = [
            self.bsugwa, self.bsuno, self.bsureligion, self.bsunation, self.bsubday,
            self.bsuage, self.bsupob, self.bsuincome
        ]

        # Basic empty-check
        missing = [w for w in required_fields if not w.text().strip()]
        if missing:
            QMessageBox.critical(self, "Missing Information", "Please fill all required fields.")
            return

        # Income validation
        income_text = self.bsuincome.text().strip()
        try:
            income_value = float(income_text)
            if income_value < 0:
                raise ValueError()
        except ValueError:
            QMessageBox.critical(self, "Invalid Income", "Annual Income must be a valid non-negative number.")
            return

        gwa_text = self.bsugwa.text().strip().replace(",", ".")
        try:
            gwa_value = float(gwa_text)
            if not (0.0 <= gwa_value <= 5.0):
                raise ValueError()
        except ValueError:
            QMessageBox.critical(self, "Invalid GWA", "Your GWA must be a valid number between 0.0 and 5.0.")
            return

        if gwa_value > 2.5:
            QMessageBox.critical(self, "Not Qualified", "Your GWA exceeds the allowed limit (2.5).")
            return

        self.finish.setEnabled(True)
        self.bsustacks.setCurrentIndex(4)

    def confirmsubmit(self, scholarship_name=None, status="PENDING", gwa_text=None):
        if not self.user_info:
            QMessageBox.critical(self, "Error", "User information not loaded.")
            return

        self.bsuconfirm.setEnabled(False)
        self.bsusubmit.setEnabled(False)
        self.finish.setEnabled(False)

        try:
            info = self.user_info
            first_name = info[6]
            last_name = info[7]
            middle_name = info[8]
            suffix = info[9] if info[9] else ""
            email = info[3]
            municipality = info[18]
            college = info[15]
            program = info[17]
            year_level = info[16]

            can_apply = database.submitvalidator(self.username, scholarship_name=scholarship_name)
            if not can_apply:
                QMessageBox.warning(self, "Duplicate Application", f"You already applied to {scholarship_name}.")
                return

            success = database.sumbitScholarship(
                username=self.username,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                suffix=suffix,
                email=email,
                municipality=municipality,
                college=college,
                program=program,
                year_level=year_level,
                scholarship_name=scholarship_name,
                status=status,
                gwa=gwa_text
            )

            if not success:
                QMessageBox.warning(self, "Submission Failed", "Failed to submit scholarship. Please try again.")
                return

            QMessageBox.information(self, "Success", f"{scholarship_name} application submitted successfully.")
            self.stacks.setCurrentIndex(1)
            self.bsustacks.setCurrentIndex(0)
            self.update_scholar_status()

            self.bsuconfirm.setEnabled(False)
            self.bsusubmit.setEnabled(False)
            self.finish.setEnabled(False)

        except Exception as e:
            print(f"Error during scholarship submission: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to submit application: {e}")
            # re-enable so user can try again
            self.bsuconfirm.setEnabled(True)
            self.bsusubmit.setEnabled(True)
            self.finish.setEnabled(True)

    ########################################################### Load user info
    def setup_user_info(self):
        self.user_info = database.handle_information_data(usernameoremail=self.username)

        if not self.user_info:
            if self.app_manager:
                self.app_manager.show_login()
            else:
                print("Error: User info not loaded, and AppManager is not available for redirect.")
            return

        fullname = " ".join([
            self.user_info[6] or "",
            self.user_info[8] or "",
            self.user_info[7] or "",
            self.user_info[9] if self.user_info[9] else ""
        ]).replace("  ", " ").strip()
        cpy = " - ".join([
            (self.user_info[15] or ""),
            (self.user_info[17] or ""),
            (self.user_info[16] or "")
        ]).strip()

        self.userprofilename.setText(fullname)
        self.cpy.setText(cpy)
        self.useremail.setText(self.user_info[3] or "")

        profile_blob = self.user_info[5]
        if profile_blob:
            for label in [self.userProfile, self.userProfile2, self.userProfile3]:
                w, h = label.width(), label.height()
                pixmap = get_rounded_stretched_pixmap(profile_blob, w, h)
                if pixmap:
                    label.setPixmap(pixmap)

    ########################################################### Dashboard Area
    def update_scholar_status(self):
        display_scholarships_util(
            username=self.username,
            scroll_area=self.ProfileScrollArea,
            database=database
        )
        self.setup_user_info()
        self._refresh_dashboard_chart()

    def _on_tab_changed(self, index):
        DASHBOARD_TAB_INDEX = 2
        if index == DASHBOARD_TAB_INDEX:
            self._refresh_dashboard_chart()

    def _refresh_dashboard_chart(self, new_data=None):
        data, studentcount, bymunicipal = database.get_all_scholars()
        data2, studentcount2, byprogram = database.get_scholarship_program_stats()
        colors = ["#E74C3C", "#2ECC71"]

        if not self.dashboard1.layout():
            self.dashboard1.setLayout(QVBoxLayout())
        try:
            barchart = create_bar_chart_widget(data=bymunicipal, title="MUNICIPALITY", colors=colors)
            barchart2 = create_bar_chart_widget(data=byprogram, title="ACCOUNTS PER MUNICIPALITY")
            add_chart_to_dashboard(self.dashboardBar3, barchart2)
            add_chart_to_dashboard(self.dashboardBar, barchart)

            # keep your naming for the labels
            self.totalAcc.setText(str(studentcount[0]))
            self.totalScholars.setText(str(data.get('SCHOLAR', 0)))
            self.totalNonScholars.setText(str(data.get('NON-SCHOLAR', 0)))
            all_scholars = create_donut_chart_widget(data=data, title="ALL SCHOLARS")
            add_chart_to_dashboard(self.dashboard1, all_scholars)
            self.interactive_dashboard()


        except Exception as e:
            print(f"Error during chart creation: {e}")

    def interactive_dashboard(self):
        data = None
        title = "DEFAULT DASHBOARD VIEW"

        SCHOLARSHIP_MAP = {
            self.SBCD: "BCD SCHOLARSHIP",
            self.SBSU: "BSU FINANCIAL ASSISTANCE",
            self.SDSWD: "DSWD EDUCATIONAL ASSISTANCE",
        }
        COLLEGE_BUTTONS = [self.SCICS, self.SCTE, self.SCHS, self.SCAS, self.SCAB, self.SCCJE]
        COLLEGE_NAME_MAP = {
            self.SCICS: "CICS", self.SCTE: "CTE", self.SCHS: "CHS",
            self.SCAS: "CAS", self.SCAB: "CABEIHM", self.SCCJE: "CCJE"
        }

        is_snone_checked = self.SNone.isChecked()
        for button in COLLEGE_BUTTONS:
            button.setDisabled(is_snone_checked)

        if is_snone_checked:
            data, _, _ = database.get_scholarship_program_stats()
            title = "INTERACTIVE DASHBOARD SCHOLARSHIPS"

        else:
            for sch_button, sch_name in SCHOLARSHIP_MAP.items():
                if sch_button.isChecked():
                    data = database.filter_by_scholarship(scholarship_name=sch_name)
                    title = f"{sch_name} BY COLLEGE"

                    for col_button, col_name in COLLEGE_NAME_MAP.items():
                        if col_button.isChecked():
                            data = database.filter_by_college(
                                scholarship_name=sch_name,
                                college_name=col_name
                            )
                            title = f"{sch_name} PROGRAMS IN {col_name}"
                            break
                    break

        if data is not None and data:
            intGraph = create_bar_chart_widget2(data=data, title=title)
            add_chart_to_dashboard(self.dashboardBar4, intGraph)
        elif data == {}:
            pass

    ########################################################### Refresh Updated Data
    def reset_scholarship_form(self):
        self.bsugwa.clear()
        self.bsuno.clear()
        self.bsureligion.clear()
        self.bsunation.clear()
        self.bsubday.clear()
        self.bsuage.clear()
        self.bsupob.clear()
        self.bsuincome.clear()

        # Re-enable buttons every time form opens
        self.bsusubmit.setEnabled(True)
        self.checkBox.setChecked(False)

        # Go back to first page of scholarship stack
        self.bsustacks.setCurrentIndex(0)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.showMaximized()
    sys.exit(app.exec_())

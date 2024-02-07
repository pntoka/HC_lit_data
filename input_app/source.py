from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QComboBox, QVBoxLayout, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import sys
import json
import os

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HC data input")
        
        # Create widgets for DOI entry
        doi_layout = QFormLayout()
        doi_title = QLabel("DOI entry & search")
        doi_layout.addWidget(doi_title)
        doi_layout.addRow("DOI:", QLineEdit())

        # Create widgets for half-cell data
        hcell_layout = QFormLayout()           
        hcell_title = QLabel("Cell data")
        hcell_layout.addWidget(hcell_title)
        hcell_layout.addRow("Coin cell type:", QLineEdit())
        hcell_layout.addRow("Cathode:", QLineEdit())
        hcell_layout.addRow("Active %:", QLineEdit())
        
        self.binder_field_layout = QVBoxLayout() # Add binder fields
        self.add_binder()

        # Create add binder button
        self.add_binder_button = QPushButton("Add Binder")
        self.add_binder_button.clicked.connect(self.add_binder)

        # Combine all left layout
        left_layout = QVBoxLayout()         
        left_layout.addLayout(doi_layout)
        left_layout.addLayout(hcell_layout)
        left_layout.addLayout(self.binder_field_layout)
        left_layout.addWidget(self.add_binder_button)  #add binder button to layout

        # Create widgets for characterization and echem data
        self.char_layout = QVBoxLayout()
        self.add_set()

        self.add_set_button = QPushButton("Add Set")
        self.add_set_button.clicked.connect(self.add_set)

        self.save_button = QPushButton("Save Data")
        self.save_button.clicked.connect(self.save_data)
        
        # Combine all right layout
        right_layout = QVBoxLayout()
        right_layout.addLayout(self.char_layout)
        right_layout.addWidget(self.add_set_button)
        right_layout.addWidget(self.save_button)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

    def add_binder(self):
        binder_layout = QHBoxLayout()

        binder_type_label = QLabel("Binder type:")
        binder_type_entry = QLineEdit()

        binder_amount_label = QLabel("Binder %wt:")
        binder_amount_entry = QLineEdit()

        binder_layout.addWidget(binder_type_label)
        binder_layout.addWidget(binder_type_entry)
        binder_layout.addWidget(binder_amount_label)
        binder_layout.addWidget(binder_amount_entry)

        self.binder_field_layout.addLayout(binder_layout)

    def add_set(self):
        set_layout = QGridLayout()
        
        precursor_label = QLabel("Precursor:")
        precursor_entry = QLineEdit()
        
        temp_label = QLabel("Temp:")
        temp_entry = QLineEdit()

        d_label = QLabel("d002:")
        d_entry = QLineEdit()

        la_label = QLabel("La:")
        la_entry = QLineEdit()

        lc_label = QLabel("Lc:")
        lc_entry = QLineEdit()

        comboBox = QComboBox()
        comboBox.addItem('ID/IG')
        comboBox.addItem('IG/ID')

        raman_entry = QLineEdit()

        # ig_id_label = QLabel("Ig/Id:")
        # ig_id_entry = QLineEdit()

        # id_ig_label = QLabel("Id/Ig:")
        # id_ig_entry = QLineEdit()

        ssa_label = QLabel("SSA:")
        ssa_entry = QLineEdit()

        ice_label = QLabel("ICE:")
        ice_entry = QLineEdit()

        cap_label = QLabel("Capacity:")
        cap_entry = QLineEdit()

        current_label = QLabel("Current:")
        current_entry = QLineEdit()
        
        set_layout.addWidget(precursor_label, 0,0)
        set_layout.addWidget(precursor_entry, 0,1)
        set_layout.addWidget(temp_label, 0,2)
        set_layout.addWidget(temp_entry, 0,3)
        set_layout.addWidget(d_label, 0,4)
        set_layout.addWidget(d_entry, 0,5)
        set_layout.addWidget(la_label, 0,6)
        set_layout.addWidget(la_entry, 0,7)
        set_layout.addWidget(lc_label, 0,8)
        set_layout.addWidget(lc_entry, 0,9)
        set_layout.addWidget(comboBox, 1,0)
        set_layout.addWidget(raman_entry, 1,1)
        set_layout.addWidget(ssa_label, 1,2)
        set_layout.addWidget(ssa_entry, 1,3)
        set_layout.addWidget(ice_label, 1,4)
        set_layout.addWidget(ice_entry, 1,5)
        set_layout.addWidget(cap_label, 1,6)
        set_layout.addWidget(cap_entry, 1,7)
        set_layout.addWidget(current_label, 1,8)
        set_layout.addWidget(current_entry, 1,9)

        self.char_layout.addLayout(set_layout)
        
    def save_data(self):
        doi = self.doi_entry.text()
        data = {"DOI": doi, "data": []}
        
        for i in range(self.field_sets_layout.count()):
            set_layout = self.field_sets_layout.itemAt(i)
            precursor_entry = set_layout.itemAt(0).widget()
            temp_entry = set_layout.itemAt(2).widget()
            capacity_entry = set_layout.itemAt(4).widget()
            precursor = precursor_entry.text()
            temp = temp_entry.text()
            capacity = capacity_entry.text()
            data["data"].append({"Precursor": precursor, "Temp": temp, "Capacity": capacity})
        
        # Example of saving to file
        try:
            with open("data.json", "w") as f:
                json.dump(data, f, indent=4)
            QMessageBox.information(self, "Success", "Data saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving data: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

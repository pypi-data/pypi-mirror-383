"""Card for stochastic site doping based on user-defined rules."""

import json
from itertools import combinations

import numpy as np
from PySide6.QtWidgets import QFrame, QGridLayout
from qfluentwidgets import BodyLabel, ComboBox, ToolTipFilter, ToolTipPosition, CheckBox, EditableComboBox

from NepTrainKit.core import CardManager
from NepTrainKit.ui.widgets import SpinBoxUnitInputFrame, DopingRulesWidget
from NepTrainKit.ui.widgets import MakeDataCard
from scipy.stats.qmc import Sobol


def sample_dopants(dopant_list, ratios, N, exact=False, seed=None):
    """Sample dopant species according to the requested ratios.

    Parameters
    ----------
    dopant_list : list
        Candidate dopant identifiers.
    ratios : list[float]
        Probabilities associated with the dopants; values are normalised internally.
    N : int
        Number of samples to draw.
    exact : bool, optional
        If ``True`` the dopant counts follow the ratios as closely as possible;
        otherwise each draw is independent.
    seed : int or None, optional
        Random seed supplied to NumPy for reproducibility.

    Returns
    -------
    list
        Sequence of dopant identifiers of length ``N``.
    """
    if seed is not None:
        np.random.seed(seed)

    dopant_list = list(dopant_list)
    ratios = np.array(ratios, dtype=float)
    ratios = ratios / ratios.sum()

    if not exact:
        return list(np.random.choice(dopant_list, size=N, p=ratios))
    else:
        counts = (ratios * N).astype(int)
        diff = N - counts.sum()
        if diff != 0:
            max_idx = np.argmax(ratios)
            counts[max_idx] += diff

        arr = np.repeat(dopant_list, counts)
        np.random.shuffle(arr)
        return list(arr)


@CardManager.register_card

class RandomDopingCard(MakeDataCard):
    """Perform random atomic substitutions according to user-specified doping rules.
    
    Parameters
    ----------
    parent : QWidget, optional
        Parent widget that owns the card controls.
    """

    group = "Defect"
    card_name = "Random Doping"
    menu_icon = r":/images/src/images/defect.svg"

    def __init__(self, parent=None):
        """Initialise the card and build its configuration widgets.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget passed to the base card constructor.
        """
        super().__init__(parent)
        self.setTitle("Random Doping Replacement")
        self.init_ui()

    def init_ui(self):
        """Build the form controls that expose the card configuration.
        """
        self.setObjectName("random_doping_card_widget")


        self.rules_label = BodyLabel("Rules", self.setting_widget)
        self.rules_widget = DopingRulesWidget(self.setting_widget)
        self.rules_label.setToolTip("doping rules")
        self.rules_label.installEventFilter(ToolTipFilter(self.rules_label, 300, ToolTipPosition.TOP))

        self.doping_label = BodyLabel("Doping", self.setting_widget)

        self.doping_type_combo=ComboBox(self.setting_widget)
        self.doping_type_combo.addItem("Random")
        self.doping_type_combo.addItem("Exact")
        self.doping_label.setToolTip("Select doping algorithm")
        self.doping_label.installEventFilter(ToolTipFilter(self.doping_label, 300, ToolTipPosition.TOP))

        self.max_atoms_label = BodyLabel("Max structures", self.setting_widget)
        self.max_atoms_condition_frame = SpinBoxUnitInputFrame(self)
        self.max_atoms_condition_frame.set_input("unit", 1)
        self.max_atoms_condition_frame.setRange(1, 10000)
        self.max_atoms_label.setToolTip("Number of structures to generate")
        self.max_atoms_label.installEventFilter(ToolTipFilter(self.max_atoms_label, 300, ToolTipPosition.TOP))

        self.settingLayout.addWidget(self.rules_label, 0, 0, 1, 1)
        self.settingLayout.addWidget(self.rules_widget, 0, 1, 1, 2)
        self.settingLayout.addWidget(self.doping_label, 1, 0, 1, 1)
        self.settingLayout.addWidget(self.doping_type_combo, 1, 1, 1, 2)
        self.settingLayout.addWidget(self.max_atoms_label, 2, 0, 1, 1)
        self.settingLayout.addWidget(self.max_atoms_condition_frame, 2, 1, 1, 2)

    def process_structure(self, structure):
        """Apply stochastic dopant replacements according to the configured rules.
        
        Parameters
        ----------
        structure : ase.Atoms
            Structure to modify.
        
        Returns
        -------
        list[ase.Atoms]
            Doped structures that satisfy the user-defined rules.
        """
        structure_list = []

        rules = self.rules_widget.to_rules()
        if not isinstance(rules, list) or not rules:
            return [structure]

        max_num = int(self.max_atoms_condition_frame.get_input_value()[0])
        exact = self.doping_type_combo.currentText()=="Exact"
        for _ in range(max_num):
            new_structure = structure.copy()
            total_doping = 0
            for rule in rules:

                target = rule.get("target")
                dopants = rule.get("dopants", {})
                if not target or not dopants:
                    continue

                groups = rule.get("group")

                if groups and "group" in new_structure.arrays:

                    candidate_indices = [i for i,elem,g in zip(range(len(new_structure)), new_structure ,new_structure.arrays["group"]) if elem.symbol == target and g in groups]
                else:
                    candidate_indices = [i for i, a in enumerate(new_structure) if a.symbol == target]

                if not candidate_indices:
                    continue

                if "concentration" == rule["use"]:
                    conc_min, conc_max = rule.get("concentration", [0.0, 1.0])
                    conc = np.random.uniform(float(conc_min), float(conc_max))
                    doping_num = max(1, int(len(candidate_indices) * conc))
                elif "count" == rule["use"]:
                    count_min, count_max = rule.get("count", [1, 1])
                    doping_num = np.random.randint(int(count_min), int(count_max) + 1)
                else:
                    doping_num = len(candidate_indices)

                doping_num = min(doping_num, len(candidate_indices))

                idxs = np.random.choice(candidate_indices, doping_num, replace=False)



                dopant_list = list(dopants.keys())
                ratios = np.array(list(dopants.values()), dtype=float)
                ratios = ratios / ratios.sum()
                sample = sample_dopants(dopant_list,ratios,doping_num,exact )


                for idx,elem in zip(idxs,sample):
                    new_structure[idx].symbol = elem
                total_doping += doping_num
            if total_doping:
                new_structure.info["Config_type"] = new_structure.info.get("Config_type", "") + f" Doping(num={total_doping})"

            structure_list.append(new_structure)

        return structure_list

    def to_dict(self):
        """Serialize the current configuration to a plain dictionary.
        
        Returns
        -------
        dict
            Dictionary that can be fed into ``from_dict`` to rebuild the state.
        """
        data_dict = super().to_dict()

        data_dict['rules'] = json.dumps(self.rules_widget.to_rules(), ensure_ascii=False)
        data_dict['doping_type'] = self.doping_type_combo.currentText()
        data_dict['max_atoms_condition'] = self.max_atoms_condition_frame.get_input_value()
        return data_dict

    def from_dict(self, data_dict):
        """Restore the card configuration from serialized values.
        
        Parameters
        ----------
        data_dict : dict
            Serialized configuration previously produced by ``to_dict``.
        """
        super().from_dict(data_dict)

        rules = data_dict.get('rules', '')
        if isinstance(rules, str):
            try:
                rules = json.loads(rules)
            except Exception:
                rules = []
        self.rules_widget.from_rules(rules)
        self.doping_type_combo.setCurrentText(data_dict.get("doping_type","Exact"))
        self.max_atoms_condition_frame.set_input_value(data_dict.get('max_atoms_condition', [1]))



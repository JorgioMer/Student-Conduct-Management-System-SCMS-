# =============================================================================
#  SCMS — Chart Widgets — Reusable chart components with auto-update
# =============================================================================
import matplotlib
# Ensure a Qt-compatible backend; avoid pyplot to reduce side effects.
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

from ui.styles import GREEN_SLIP, PINK_SLIP, BLUE_SLIP, NAVY, OFF_WHITE


class MatplotlibChart(QWidget):
    """Base class for matplotlib-based charts embedded in PyQt5."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(10, 4), dpi=100, facecolor=OFF_WHITE)
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def clear_figure(self):
        """Clear all axes from the figure."""
        self.figure.clear()
    
    def refresh(self):
        """Override in subclasses to update chart data."""
        self.figure.canvas.draw()


class GreenSlipChart(MatplotlibChart):
    """Chart showing Green Slip distribution."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure.set_facecolor(OFF_WHITE)
    
    def update_data(self, dispensation_count, excuse_count, active_count, expired_count):
        """Update chart with new data."""
        self.clear_figure()
        
        # Create 2 subplots
        ax1 = self.figure.add_subplot(121)
        ax2 = self.figure.add_subplot(122)
        
        # Left: Pie chart - Dispensation vs Excuse
        labels1 = []
        sizes1 = []
        colors1 = []
        if dispensation_count > 0:
            labels1.append(f'Dispensation ({dispensation_count})')
            sizes1.append(dispensation_count)
            colors1.append('#388E3C')
        if excuse_count > 0:
            labels1.append(f'Excuse ({excuse_count})')
            sizes1.append(excuse_count)
            colors1.append('#66BB6A')
        
        if sizes1:
            ax1.pie(sizes1, labels=labels1, colors=colors1, autopct='%1.1f%%', 
                   startangle=90, textprops={'fontsize': 10, 'weight': 'bold'})
            ax1.set_title('Green Slips: Dispensation vs Excuse', fontsize=11, fontweight='bold', pad=15)
        else:
            ax1.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=12)
            ax1.set_title('Green Slips: Dispensation vs Excuse', fontsize=11, fontweight='bold', pad=15)
            ax1.set_xlim(0, 1)
            ax1.set_ylim(0, 1)
        
        # Right: Bar chart - Status distribution
        statuses = ['Active', 'Expired']
        counts = [active_count, expired_count]
        bars = ax2.bar(statuses, counts, color=['#4CAF50', '#FF9800'], edgecolor='black', linewidth=1.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        ax2.set_ylabel('Count', fontsize=10, fontweight='bold')
        ax2.set_title('Green Slips by Status', fontsize=11, fontweight='bold', pad=15)
        ax2.set_ylim(0, max(counts) * 1.15 if counts else 1)
        ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        
        self.figure.tight_layout()
        self.canvas.draw()


class BlueSlipChart(MatplotlibChart):
    """Chart showing Blue Slip violation distribution."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure.set_facecolor(OFF_WHITE)
    
    def update_data(self, violation_types, pending_count, escalated_count, resolved_count):
        """Update chart with new data.
        
        Args:
            violation_types: dict mapping violation type -> count
            pending_count: number of pending violations
            escalated_count: number of escalated cases
            resolved_count: number of resolved cases
        """
        self.clear_figure()
        
        # Left: Bar chart - Violations by type
        ax1 = self.figure.add_subplot(121)
        
        if violation_types:
            types = list(violation_types.keys())[:8]  # Limit to 8 types
            counts = [violation_types[t] for t in types]
            colors_list = [BLUE_SLIP if i % 2 == 0 else '#64B5F6' for i in range(len(types))]
            bars = ax1.bar(range(len(types)), counts, color=colors_list, edgecolor='black', linewidth=1.5)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}',
                            ha='center', va='bottom', fontweight='bold', fontsize=9)
            
            ax1.set_xticks(range(len(types)))
            ax1.set_xticklabels(types, rotation=45, ha='right', fontsize=9)
            ax1.set_ylabel('Count', fontsize=10, fontweight='bold')
            ax1.set_title('Violations by Type', fontsize=11, fontweight='bold', pad=15)
            ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax1.grid(axis='y', alpha=0.3, linestyle='--')
            ax1.set_ylim(0, max(counts) * 1.15 if counts else 1)
        else:
            ax1.text(0.5, 0.5, 'No violation data', ha='center', va='center', fontsize=12)
            ax1.set_title('Violations by Type', fontsize=11, fontweight='bold', pad=15)
            ax1.set_xlim(0, 1)
            ax1.set_ylim(0, 1)
        
        # Right: Pie chart - Status distribution
        ax2 = self.figure.add_subplot(122)
        labels2 = []
        sizes2 = []
        colors2 = []
        
        if pending_count > 0:
            labels2.append(f'Pending ({pending_count})')
            sizes2.append(pending_count)
            colors2.append('#F57F17')
        if escalated_count > 0:
            labels2.append(f'Escalated ({escalated_count})')
            sizes2.append(escalated_count)
            colors2.append('#D32F2F')
        if resolved_count > 0:
            labels2.append(f'Resolved ({resolved_count})')
            sizes2.append(resolved_count)
            colors2.append('#2E7D32')
        
        if sizes2:
            ax2.pie(sizes2, labels=labels2, colors=colors2, autopct='%1.1f%%',
                   startangle=90, textprops={'fontsize': 10, 'weight': 'bold'})
            ax2.set_title('Violations by Status', fontsize=11, fontweight='bold', pad=15)
        else:
            ax2.text(0.5, 0.5, 'No status data', ha='center', va='center', fontsize=12)
            ax2.set_title('Violations by Status', fontsize=11, fontweight='bold', pad=15)
            ax2.set_xlim(0, 1)
            ax2.set_ylim(0, 1)
        
        self.figure.tight_layout()
        self.canvas.draw()


class PinkSlipChart(MatplotlibChart):
    """Chart showing Pink Slip violation distribution."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure.set_facecolor(OFF_WHITE)
    
    def update_data(self, violation_types, year_distribution):
        """Update chart with new data.
        
        Args:
            violation_types: dict mapping violation type -> count
            year_distribution: dict mapping year level -> count
        """
        self.clear_figure()
        
        # Left: Bar chart - Violations by type
        ax1 = self.figure.add_subplot(121)
        
        if violation_types:
            types = list(violation_types.keys())[:8]  # Limit to 8 types
            counts = [violation_types[t] for t in types]
            colors_list = [PINK_SLIP if i % 2 == 0 else '#F48FB1' for i in range(len(types))]
            bars = ax1.bar(range(len(types)), counts, color=colors_list, edgecolor='black', linewidth=1.5)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}',
                            ha='center', va='bottom', fontweight='bold', fontsize=9)
            
            ax1.set_xticks(range(len(types)))
            ax1.set_xticklabels(types, rotation=45, ha='right', fontsize=9)
            ax1.set_ylabel('Count', fontsize=10, fontweight='bold')
            ax1.set_title('Pink Slips by Violation Type', fontsize=11, fontweight='bold', pad=15)
            ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax1.grid(axis='y', alpha=0.3, linestyle='--')
            ax1.set_ylim(0, max(counts) * 1.15 if counts else 1)
        else:
            ax1.text(0.5, 0.5, 'No violation data', ha='center', va='center', fontsize=12)
            ax1.set_title('Pink Slips by Violation Type', fontsize=11, fontweight='bold', pad=15)
            ax1.set_xlim(0, 1)
            ax1.set_ylim(0, 1)
        
        # Right: Pie chart - Grade level distribution
        ax2 = self.figure.add_subplot(122)
        
        if year_distribution:
            years = list(year_distribution.keys())
            counts = [year_distribution[y] for y in years]
            colors_list = ['#FF6F00', '#FF8A50', '#FFB74D', '#FFCC80', '#FFE0B2'][:len(years)]
            
            ax2.pie(counts, labels=years, colors=colors_list, autopct='%1.1f%%',
                   startangle=90, textprops={'fontsize': 10, 'weight': 'bold'})
            ax2.set_title('Pink Slips by Grade Level', fontsize=11, fontweight='bold', pad=15)
        else:
            ax2.text(0.5, 0.5, 'No grade data', ha='center', va='center', fontsize=12)
            ax2.set_title('Pink Slips by Grade Level', fontsize=11, fontweight='bold', pad=15)
            ax2.set_xlim(0, 1)
            ax2.set_ylim(0, 1)
        
        self.figure.tight_layout()
        self.canvas.draw()


class CombinedAllSlipsChart(MatplotlibChart):
    """Chart showing combined Green, Pink, and Blue slip distribution."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure.set_facecolor(OFF_WHITE)
    
    def update_data(self, green_count, pink_count, blue_count):
        """Update chart with new data for all slip types.
        
        Args:
            green_count: number of green slips
            pink_count: number of pink slips  
            blue_count: number of blue slips
        """
        self.clear_figure()
        
        # Left: Pie chart - All slip types
        ax1 = self.figure.add_subplot(121)
        
        labels = []
        sizes = []
        colors = []
        
        if green_count > 0:
            labels.append(f'Green ({green_count})')
            sizes.append(green_count)
            colors.append(GREEN_SLIP)
        if pink_count > 0:
            labels.append(f'Pink ({pink_count})')
            sizes.append(pink_count)
            colors.append(PINK_SLIP)
        if blue_count > 0:
            labels.append(f'Blue ({blue_count})')
            sizes.append(blue_count)
            colors.append(BLUE_SLIP)
        
        if sizes:
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                   startangle=90, textprops={'fontsize': 10, 'weight': 'bold'})
            ax1.set_title('All Slip Records by Type', fontsize=11, fontweight='bold', pad=15)
        else:
            ax1.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=12)
            ax1.set_title('All Slip Records by Type', fontsize=11, fontweight='bold', pad=15)
            ax1.set_xlim(0, 1)
            ax1.set_ylim(0, 1)
        
        # Right: Bar chart - Comparison by type
        ax2 = self.figure.add_subplot(122)
        
        slip_types = ['Green', 'Pink', 'Blue']
        counts = [green_count, pink_count, blue_count]
        bar_colors = [GREEN_SLIP, PINK_SLIP, BLUE_SLIP]
        
        bars = ax2.bar(slip_types, counts, color=bar_colors, edgecolor='black', linewidth=1.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        ax2.set_ylabel('Count', fontsize=10, fontweight='bold')
        ax2.set_title('Total Monthly Records by Type', fontsize=11, fontweight='bold', pad=15)
        ax2.set_ylim(0, max(counts) * 1.15 if counts else 1)
        ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        
        self.figure.tight_layout()
        self.canvas.draw()

# Prime Players Football Analytics Center

A comprehensive football analytics dashboard built with Next.js, featuring advanced metrics and data visualization for talent development analysis.

## 🚀 Features

### 📊 **Advanced Analytics Dashboard**

- **Home Page**: Overview with key metrics and futuristic bar charts
- **Training Club and Players**: Detailed player database with advanced filtering
- **Development Analysis**: Youth development metrics and club performance
- **Geographic Analysis**: Talent migration patterns and regional insights
- **Performance Metrics**: Development efficiency and retention rates
- **Predictive Analytics**: Future star potential and market value predictions

### 🎨 **Modern UI/UX**

- **Dark Theme**: Linear-inspired minimalist design
- **Futuristic Charts**: Animated bar charts with gradients and effects
- **Responsive Design**: Optimized for all screen sizes
- **Custom Logo**: Branded with Prime Players identity

### 📈 **Data Insights**

- **25,118+ Players**: Comprehensive database with enriched data
- **8,208+ Training Clubs**: Global coverage of youth academies
- **40+ Countries**: International talent analysis
- **Advanced Metrics**: 20+ calculated indices and scores

## 🛠️ Technology Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS, shadcn/ui components
- **Data Processing**: PapaParse for CSV handling
- **Icons**: Lucide React
- **Deployment**: Vercel-ready

## 📁 Repository Structure

```
football-analytics-dashboard/
├── src/
│   ├── app/                    # Next.js app router pages
│   │   ├── page.tsx           # Home page
│   │   ├── players/           # Players database page
│   │   ├── development/       # Development analysis
│   │   ├── geographic/        # Geographic analysis
│   │   ├── performance/       # Performance metrics
│   │   └── predictive/        # Predictive analytics
│   ├── components/            # Reusable UI components
│   │   ├── sidebar.tsx        # Navigation sidebar
│   │   └── logo.tsx           # Custom logo component
│   ├── hooks/                 # Custom React hooks
│   │   └── usePlayerData.ts   # Data loading and processing
│   └── lib/                   # Utility functions
├── public/
│   ├── data.csv              # Main dataset
│   └── logo.png              # Application logo
└── db-old/                   # Database files (gitignored except main CSV)
    └── db_football_training_clubs.csv
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd football-analytics
   ```

2. **Install dependencies**

   ```bash
   cd football-analytics-dashboard
   npm install
   ```

3. **Run the development server**

   ```bash
   npm run dev
   ```

4. **Open your browser**
   Navigate to [http://localhost:3090](http://localhost:3090)

### Production Build

```bash
npm run build
npm start
```

## 📊 Data Sources

The application uses enriched football data including:

- **Player Information**: Names, positions, nationalities, market values
- **Training Clubs**: Youth academy affiliations and countries
- **Transfer Data**: Latest transfers and market values
- **Geographic Data**: Country mappings and regional analysis

## 🎯 Key Metrics

### Development Analysis

- **Youth Development Index**: Country-level development scoring
- **Club Development Score**: Academy performance metrics
- **Talent Pipeline Strength**: Age group distribution analysis
- **Geographic Talent Density**: Regional talent concentration

### Geographic Analysis

- **Talent Migration Patterns**: Cross-border development flows
- **Regional Development Centers**: Geographic talent hubs
- **Cross-Border Development**: International academy usage
- **Talent Export/Import Ratio**: Country talent balance

### Performance Metrics

- **Development Efficiency**: Value per development year
- **Talent Retention Rate**: Local vs international development
- **Club Success Correlation**: Academy-to-professional success
- **Age-to-Value Ratio**: Performance by age groups

### Predictive Analytics

- **Future Star Potential**: Young talent identification
- **Development Trajectory**: Career path predictions
- **Market Value Prediction**: Financial value forecasting
- **Talent Scouting Score**: Recruitment effectiveness

## 🔧 Configuration

### Environment Variables

No environment variables required for basic functionality.

### Data Updates

To update the dataset:

1. Replace `public/data.csv` with new data
2. Ensure column structure matches the expected format
3. Restart the development server

## 📱 Deployment

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Deploy automatically on push to main branch
3. Configure build settings if needed

### Other Platforms

The application is a standard Next.js app and can be deployed to:

- Netlify
- AWS Amplify
- Railway
- Any Node.js hosting platform

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🎉 Acknowledgments

- Data sourced from Transfermarkt and other public football databases
- UI inspired by Linear's design system
- Built with modern web technologies for optimal performance

---

**Prime Players Football Analytics Center** - Advanced insights for football talent development 🚀⚽

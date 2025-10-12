use exact_clustering_rs::{Cost, Point, WeightedPoint};
use ndarray::prelude::*;
use pyo3::{exceptions::PyValueError, prelude::*};
use pyo3_stub_gen::{
    define_stub_info_gatherer,
    derive::{gen_stub_pyclass, gen_stub_pymethods},
};

struct ClusteringInstance<T: Cost>(T);
impl<T: Cost> ClusteringInstance<T> {
    fn price_of_hierarchy(&mut self) -> f64 {
        self.0.price_of_hierarchy().0
    }

    fn price_of_greedy(&mut self) -> f64 {
        self.0.price_of_greedy().0
    }
}

macro_rules! unweighted {
    ($name: ident, $type: path, $constructor: path) => {
        #[gen_stub_pyclass]
        #[pyclass]
        pub struct $name(ClusteringInstance<$type>);

        #[gen_stub_pymethods]
        #[pymethods]
        impl $name {
            #[new]
            pub fn new(data: Vec<Vec<f64>>) -> PyResult<Self> {
                let instance = $constructor(&to_points(data))
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                Ok(Self(ClusteringInstance(instance)))
            }

            fn price_of_hierarchy(&mut self) -> f64 {
                self.0.price_of_hierarchy()
            }

            fn price_of_greedy(&mut self) -> f64 {
                self.0.price_of_greedy()
            }
        }
    };
}
macro_rules! weighted {
    ($name: ident, $type: path, $constructor: path) => {
        #[gen_stub_pyclass]
        #[pyclass]
        pub struct $name(ClusteringInstance<$type>);

        #[gen_stub_pymethods]
        #[pymethods]
        impl $name {
            #[new]
            pub fn new(data: Vec<(f64, Vec<f64>)>) -> PyResult<Self> {
                let instance = $constructor(&to_weighted_points(data))
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                Ok(Self(ClusteringInstance(instance)))
            }

            fn price_of_hierarchy(&mut self) -> f64 {
                self.0.price_of_hierarchy()
            }

            fn price_of_greedy(&mut self) -> f64 {
                self.0.price_of_greedy()
            }
        }
    };
}

unweighted!(
    KMeans,
    exact_clustering_rs::KMeans,
    exact_clustering_rs::KMeans::new
);
weighted!(
    WeightedKMeans,
    exact_clustering_rs::WeightedKMeans,
    exact_clustering_rs::WeightedKMeans::new
);

unweighted!(
    KMedianL1,
    exact_clustering_rs::KMedian,
    exact_clustering_rs::KMedian::l1
);
unweighted!(
    KMedianL2,
    exact_clustering_rs::KMedian,
    exact_clustering_rs::KMedian::l2
);
unweighted!(
    KMedianL2Squared,
    exact_clustering_rs::KMedian,
    exact_clustering_rs::KMedian::l2_squared
);

weighted!(
    WeightedKMedianL1,
    exact_clustering_rs::KMedian,
    exact_clustering_rs::KMedian::weighted_l1
);
weighted!(
    WeightedKMedianL2,
    exact_clustering_rs::KMedian,
    exact_clustering_rs::KMedian::weighted_l2
);
weighted!(
    WeightedKMedianL2Squared,
    exact_clustering_rs::KMedian,
    exact_clustering_rs::KMedian::weighted_l2_squared
);

fn to_points(points: Vec<Vec<f64>>) -> Vec<Point> {
    points.into_iter().map(Array1::from_vec).collect()
}

fn to_weighted_points(weighted_points: Vec<(f64, Vec<f64>)>) -> Vec<WeightedPoint> {
    weighted_points
        .into_iter()
        .map(|(w, v)| (w, Array1::from_vec(v)))
        .collect()
}

#[pymodule]
fn exact_clustering(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<KMeans>()?;
    m.add_class::<WeightedKMeans>()?;
    m.add_class::<KMedianL1>()?;
    m.add_class::<KMedianL2>()?;
    m.add_class::<KMedianL2Squared>()?;
    m.add_class::<WeightedKMedianL1>()?;
    m.add_class::<WeightedKMedianL2>()?;
    m.add_class::<WeightedKMedianL2Squared>()?;
    Ok(())
}

define_stub_info_gatherer!(stub_info);

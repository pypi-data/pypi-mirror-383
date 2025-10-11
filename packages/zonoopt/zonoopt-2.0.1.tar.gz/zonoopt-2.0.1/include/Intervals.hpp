#ifndef ZONOOPT_INTERVAL_UTILITIES_HPP_
#define ZONOOPT_INTERVAL_UTILITIES_HPP_

/**
 * @file Intervals.hpp
 * @author Josh Robbins (jrobbins@psu.edu)
 * @brief Interval and box classes.
 * @version 1.0
 * @date 2025-06-04
 * 
 * @copyright Copyright (c) 2025
 * 
 */

#include <limits>
#include <string>
#include <vector>
#include <set>
#include <cmath>
#include <cassert>
#include <Eigen/Dense>
#include <Eigen/Sparse>

/*
Reference: 
"Applied Interval Analysis"
Luc Jaulin, Michel Kieffer, Olivier Didrit, Eric Walter
*/

namespace ZonoOpt {

    using namespace detail;

    // forward declarations
    struct Interval;
    struct IntervalView;


    /**
     * @brief Base class for Interval and IntervalView
     *
     * This class defines the interface for Interval and IntervalView
     * using the CRTP.
     *
     */
    template <typename Derived>
    struct IntervalBase
    {
        /**
         * @brief Returns reference to interval lower bound
         * @return reference to y_min
         */
        zono_float& y_min() { return static_cast<Derived*>(this)->get_y_min(); }

        /**
         * @brief Returns reference to interval upper bound
         * @return reference to y_max
         */
        zono_float& y_max() { return static_cast<Derived*>(this)->get_y_max(); }

        /**
         * @brief Returns const reference to interval lower bound
         * @return reference to y_min
         */
        const zono_float& y_min() const { return static_cast<const Derived*>(this)->get_y_min(); }

        /**
         * @brief Returns const reference to interval upper bound
         * @return reference to y_max
         */
        const zono_float& y_max() const { return static_cast<const Derived*>(this)->get_y_max(); }

        /**
         * @brief Sets interval bounds
         * @param min lower bound
         * @param max upper bound
         */
        void set(const zono_float min, const zono_float max)
        {
            y_min() = min;
            y_max() = max;
        }

        /**
         * @brief sets interval to x1 + x2
         * @param x1 interval
         * @param x2 interval
         */
        void add_assign(const Derived& x1, const Derived& x2)
        {
            y_min() = x1.y_min() + x2.y_min();
            y_max() = x1.y_max() + x2.y_max();
        }

        /**
         * @brief sets interval to x1 - x2
         * @param x1 interval
         * @param x2 interval
         */
        void subtract_assign(const Derived& x1, const Derived& x2)
        {
            y_min() = x1.y_min() - x2.y_max();
            y_max() = x1.y_max() - x2.y_min();
        }

        /**
         * @brief sets interval to x1 * x2
         * @param x1 interval
         * @param x2 interval
         */
        void multiply_assign(const Derived& x1, const Derived& x2)
        {
            zono_float a = x1.y_min() * x2.y_min();
            zono_float b = x1.y_min() * x2.y_max();
            zono_float c = x1.y_max() * x2.y_min();
            zono_float d = x1.y_max() * x2.y_max();

            y_min() = std::min({a, b, c, d});
            y_max() = std::max({a, b, c, d});
        }

        /**
         * @brief sets interval to alpha * x1
         * @param x1 interval
         * @param alpha scalar
         */
        void multiply_assign(const Derived& x1, zono_float alpha)
        {
            if (alpha >= 0)
            {
                y_min() = x1.y_min() * alpha;
                y_max() = x1.y_max() * alpha;
            }
            else
            {
                y_min() = x1.y_max() * alpha;
                y_max() = x1.y_min() * alpha;
            }
        }

        /**
         * @brief sets interval to its inverse
         */
        void inverse()
        {
            auto& min = y_min();
            auto& max = y_max();

            if (std::abs(min) < zono_eps && std::abs(max) < zono_eps)
            {
                min = std::numeric_limits<zono_float>::infinity();
                max = -std::numeric_limits<zono_float>::infinity();
            }
            else if (min > 0 || max < 0)
            {
                min = one / max;
                max = one / min;
            }
            else if (std::abs(min) < zono_eps && max > 0)
            {
                min = one / max;
                max = std::numeric_limits<zono_float>::infinity();
            }
            else if (min < 0 && std::abs(max) < zono_eps)
            {
                max = one / min;
                min = -std::numeric_limits<zono_float>::infinity();
            }
            else
            {
                min = -std::numeric_limits<zono_float>::infinity();
                max = std::numeric_limits<zono_float>::infinity();
            }
        }

        /**
         * @brief sets interval to x1 / x2
         * @param x1 interval
         * @param x2 interval
         */
        void divide_assign(const Derived& x1, const Derived& x2)
        {
            Derived inv = x2;
            inv.inverse();
            multiply_assign(x1, inv);
        }

        /**
         * @brief sets interval to intersection of x1 and x2
         * @param x1 interval
         * @param x2 interval
         */
        void intersect_assign(const Derived& x1, const Derived& x2)
        {
            y_min() = std::max(x1.y_min(), x2.y_min());
            y_max() = std::min(x1.y_max(), x2.y_max());
        }

        /**
         * @brief checks whether interval is empty
         * @return flag indicating if interval is empty
         */
        bool is_empty() const
        {
            return y_min() - y_max() > zono_eps;
        }

        /**
         * @brief checks whether interval contains a value
         * @param y scalar value
         * @return flag indicating if interval contains y
         */
        bool contains(zono_float y) const
        {
            return y >= y_min() - zono_eps && y <= y_max() + zono_eps;
        }

        /**
         * @brief checks whether interval is single-valued (i.e., width is 0 within numerical tolerance)
         * @return flag indicating if interval is single-value
         */
        bool is_single_valued() const
        {
            return std::abs(y_max() - y_min()) < zono_eps;
        }

        /**
         * @brief get width of interval (ub - lb)
         * @return interval width
         */
        zono_float width() const
        {
            return std::abs(y_max() - y_min());
        }

        /**
         * @brief compute interval containing sin(x) over x
         * @param x input interval
         */
        void sin_assign(const Derived& x)
        {
            if (x.y_max() - x.y_min() >= two*pi)
            {
                y_max() = one;
                y_min() = -one;
            }
            else
            {
                // shift domain to [-pi, pi]
                zono_float u = x.y_max(); // init
                zono_float l = x.y_min(); // init
                while (u > pi)
                {
                    u -= two*pi;
                    l -= two*pi;
                }
                while (l < -pi)
                {
                    u += two*pi;
                    l += two*pi;
                }

                // get bounds
                y_max() = ((l < pi/two && pi/two < u) || (l < -3*pi/two && -3*pi/two < u)) ? one : std::max(std::sin(u), std::sin(l));
                y_min() = ((l < -pi/two && -pi/two < u) || (l < 3*pi/two && 3*pi/two < u)) ? -one : std::min(std::sin(u), std::sin(l));
            }
        }

        /**
         * @brief compute interval containing cos(x) over x
         * @param x input interval
         */
        void cos_assign(const Derived& x)
        {
            Derived x_sin;
            x_sin.set(x.y_min() + pi/two, x.y_max() + pi/two);
            sin_assign(x_sin);
        }

        /**
         * @brief compute interval containing tan(x) over x
         * @param x input interval
         */
        void tan_assign(const Derived& x)
        {
            if (x.y_max() - x.y_min() >= pi)
            {
                y_max() = std::numeric_limits<zono_float>::infinity();
                y_min() = -std::numeric_limits<zono_float>::infinity();
            }
            else
            {
                // shift domain to [-pi, pi]
                zono_float u = x.y_max(); // init
                zono_float l = x.y_min(); // init
                while (u > pi)
                {
                    u -= two*pi;
                    l -= two*pi;
                }
                while (l < -pi)
                {
                    u += two*pi;
                    l += two*pi;
                }

                // get bounds
                if ((l < -pi/two && -pi/two < u) || (l < pi/two && pi/two < u))
                {
                    y_max() = std::numeric_limits<zono_float>::infinity();
                    y_min() = -std::numeric_limits<zono_float>::infinity();
                }
                else
                {
                    y_max() = std::tan(u);
                    y_min() = std::tan(l);
                }
            }
        }

        /**
         * @brief compute interval containing arcsin(x) over x
         * @param x input interval
         */
        void arcsin_assign(const Derived& x)
        {
            assert(x.y_min() >= -one && x.y_min() <= one);
            assert(x.y_max() >= -one && x.y_max() <= one);
            y_min() = std::asin(x.y_min());
            y_max() = std::asin(x.y_max());
        }

        /**
         * @brief compute interval containing arccos(x) over x
         * @param x input interval
         */
        void arccos_assign(const Derived& x)
        {
            assert(x.y_min() >= -one && x.y_min() <= one);
            assert(x.y_max() >= -one && x.y_max() <= one);
            y_min() = std::acos(x.y_max());
            y_max() = std::acos(x.y_min());
        }

        /**
         * @brief compute interval containing arctan(x) over x
         * @param x input interval
         */
        void arctan_assign(const Derived& x)
        {
            y_min() = std::atan(x.y_min());
            y_max() = std::atan(x.y_max());
        }

        /**
         * @brief compute interval containing exp(x) over x
         * @param x input interval
         */
        void exp_assign(const Derived& x)
        {
            y_min() = std::exp(x.y_min());
            y_max() = std::exp(x.y_max());
        }
    };

    /**
     * @brief Interval class
     *
     * Implements interface from IntervalBase. This class owns its lower and upper bounds.
     */
    struct Interval : IntervalBase<Interval>
    {
        // members
        /// lower bound
        zono_float lb;

        /// upper bound
        zono_float ub;

        // constructor
        /**
         * @brief default constructor
         */
        Interval() : lb(0), ub(0) {}

        /**
         * @brief Interval constructor
         * @param y_min lower bound
         * @param y_max upper bound
         */
        Interval(zono_float y_min, zono_float y_max) : lb(y_min), ub(y_max) {}

        /**
         * @brief Clone Interval object
         * @return clone of object
         */
        Interval* clone() const
        {
            return new Interval(*this);
        }

        // get methods

        /**
         * @brief get reference to lower bound
         * @return reference to lower bound
         */
        zono_float& get_y_min() { return lb; }

        /**
         * @brief get reference to upper bound
         * @return reference to upper bound
         */
        zono_float& get_y_max() { return ub; }

        /**
         * @brief get const reference to lower bound
         * @return reference to lower bound
         */
        const zono_float& get_y_min() const { return lb; }

        /**
         * @brief get const reference to upper bound
         * @return reference to upper bound
         */
        const zono_float& get_y_max() const { return ub; }

        // operators

        /**
         * @brief interval addition
         * @param other other interval
         * @return this + other
         */
        Interval operator+(const Interval& other) const
        {
            Interval result;
            result.add_assign(*this, other);
            return result;
        }

        /**
         * @brief interval subtraction
         * @param other other interval
         * @return this - other
         */
        Interval operator-(const Interval& other) const
        {
            Interval result;
            result.subtract_assign(*this, other);
            return result;
        }

        /**
         * @brief interval multiplication
         * @param other other interval
         * @return this * other
         */
        Interval operator*(const Interval& other) const
        {
            Interval result;
            result.multiply_assign(*this, other);
            return result;
        }

        /**
         * @brief interval multiplication with scalar
         * @param alpha scalar
         * @return alpha * this
         */
        Interval operator*(zono_float alpha) const
        {
            Interval result;
            result.multiply_assign(*this, alpha);
            return result;
        }

        /**
         * @brief interval inverse
         * @return inverse of this
         */
        Interval inv() const
        {
            Interval result = *this;
            result.inverse();
            return result;
        }

        /**
         * @brief interval division
         * @param other other interval
         * @return this / other
         */
        Interval operator/(const Interval& other) const
        {
            Interval result;
            result.divide_assign(*this, other);
            return result;
        }

        /**
         * @brief interval intersection
         * @param other other interval
         * @return intersection of this and other
         */
        Interval intersect(const Interval& other) const
        {
            Interval result;
            result.intersect_assign(*this, other);
            return result;
        }

        /**
         * @brief get center of interval
         * @return center of interval
         */
        zono_float center() const
        {
            return (ub + lb) / two;
        }

        // as interval view
        /**
         * @brief IntervalView interface for Interval
         * @return IntervalView of this
         */
        IntervalView as_view();

        // print methods
        /**
         * @brief print method for Interval
         * @return string representation of interval
         */
        std::string print() const
        {
            return "Interval: [" + std::to_string(lb) + ", " + std::to_string(ub) + "]";
        }

        /**
         * @brief print to ostream
         * @param os
         * @param interval
         * @return ostream reference
         */
        friend std::ostream& operator<<(std::ostream& os, const Interval& interval)
        {
            os << interval.print();
            return os;
        }

        /**
         * @brief compute interval containing sin(x) for all x in interval
         * @return interval containing sin(x)
         */
        Interval sin() const
        {
            Interval result;
            result.sin_assign(*this);
            return result;
        }

        /**
         * @brief compute interval containing cos(x) for all x in interval
         * @return interval containing cos(x)
         */
        Interval cos() const
        {
            Interval result;
            result.cos_assign(*this);
            return result;
        }

        /**
         * @brief compute interval containing tan(x) for all x in interval
         * @return interval containing tan(x)
         */
        Interval tan() const
        {
            Interval result;
            result.tan_assign(*this);
            return result;
        }

        /**
         * @brief compute interval containing arcsin(x) for all x in interval
         * @return interval containing arcsin(x)
         */
        Interval arcsin() const
        {
            Interval result;
            result.arcsin_assign(*this);
            return result;
        }

        /**
         * @brief compute interval containing arccos(x) for all x in interval
         * @return interval containing arccos(x)
         */
        Interval arccos() const
        {
            Interval result;
            result.arccos_assign(*this);
            return result;
        }

        /**
         * @brief compute interval containing arctan(x) for all x in interval
         * @return interval containing arctan(x)
         */
        Interval arctan() const
        {
            Interval result;
            result.arctan_assign(*this);
            return result;
        }

        /**
         * @brief compute interval containing exp(x) for all x in interval
         * @return interval containing exp(x)
         */
        Interval exp() const
        {
            Interval result;
            result.exp_assign(*this);
            return result;
        }
    };

    /**
     * @brief IntervalView class
     *
     * Implements interface from IntervalBase. This class does not own its lower and upper bounds.
     */
    struct IntervalView : IntervalBase<IntervalView>
    {
        // members

        /// pointer to lower bound
        zono_float* lb_ptr = nullptr;

        /// pointer to upper bound
        zono_float* ub_ptr = nullptr;

        // constructor

        /**
         * @brief constructor for IntervalView
         * @param y_min lower bound pointer
         * @param y_max upper bound pointer
         */
        IntervalView(zono_float* y_min, zono_float* y_max) : lb_ptr(y_min), ub_ptr(y_max) {}

        // assignment

        /**
         * @brief Assignment operator
         * @tparam Derived either Interval or IntervalView
         * @param other other interval
         * @return this = other
         */
        template <typename Derived>
        IntervalView& operator=(const IntervalBase<Derived>& other)
        {
            y_min() = other.y_min();
            y_max() = other.y_max();
            return *this;
        }

        // to Interval
        /**
         * @brief convert to Interval class
         * @return interval as Interval
         */
        Interval to_interval() const;

        // methods

        /**
         * @brief get reference to lower bound
         * @return reference to lower bound
         */
        zono_float& get_y_min() { return *lb_ptr; }

        /**
         * @brief get reference to upper bound
         * @return reference to upper bound
         */
        zono_float& get_y_max() { return *ub_ptr; }

        /**
         * @brief get const reference to lower bound
         * @return reference to lower bound
         */
        const zono_float& get_y_min() const { return *lb_ptr; }

        /**
         * @brief get const reference to upper bound
         * @return reference to upper bound
         */
        const zono_float& get_y_max() const { return *ub_ptr; }
    };

    // implementations
    inline Interval IntervalView::to_interval() const
    {
        return Interval(*lb_ptr, *ub_ptr);
    }

    inline IntervalView Interval::as_view()
    {
        return IntervalView(&lb, &ub);
    }

    /**
     * @brief Box (i.e., interval vector) class
     */
    class Box
    {
    public:

        // constructors

        /**
         * @brief Default constructor
         */
        Box() = default;

        /**
         * @brief Default construct with size specified
         * @param size dimension of box
         */
        explicit Box(const size_t size)
        {
            x_lb.resize(static_cast<Eigen::Index>(size));
            x_ub.resize(static_cast<Eigen::Index>(size));
        }

        /**
         * @brief Constructor using vector of intervals
         * @param vals vector of intervals
         */
        explicit Box(const std::vector<Interval>& vals)
        {
            x_lb.resize(static_cast<Eigen::Index>(vals.size()));
            x_ub.resize(static_cast<Eigen::Index>(vals.size()));

            for (Eigen::Index i=0; i<static_cast<Eigen::Index>(vals.size()); i++)
            {
                this->x_lb(i) = vals[i].y_min();
                this->x_ub(i) = vals[i].y_max();
            }
        }

        /**
         * @brief Constructor from intervals of lower and upper bounds
         * @param x_lb vector of lower bounds
         * @param x_ub vector of upper bounds
         */
        Box(const Eigen::Vector<zono_float, -1>& x_lb, const Eigen::Vector<zono_float, -1>& x_ub)
        {
            if (x_lb.size() != x_ub.size())
                throw std::invalid_argument("x_l and x_u must have the same size");
            this->x_lb = x_lb;
            this->x_ub = x_ub;
        }

        // virtual destructor
        /**
         * @brief Virtual destructor
         */
        virtual ~Box() = default;

        // copy assignment
        /**
         * @brief Copy assignment
         * @param other other Box object
         * @return this = other
         */
        Box& operator=(const Box& other)
        {
            if (this != &other)
            {
                this->x_lb = other.x_lb;
                this->x_ub = other.x_ub;
            }
            return *this;
        }

        // copy constructor
        /**
         * @brief Copy constructor
         * @param other other Box object
         */
        Box(const Box& other)
        {
            this->x_lb = other.x_lb;
            this->x_ub = other.x_ub;
        }

        // element-wise assignment, access

        /**
         * @brief Element-wise access, used for assignment
         * @param i index
         * @return IntervalView for element i in Box
         */
        IntervalView operator[](const size_t i)
        {
            if (i >= static_cast<size_t>(x_lb.size()))
                throw std::out_of_range("Index out of range");
            return IntervalView(&x_lb(static_cast<Eigen::Index>(i)), &x_ub(static_cast<Eigen::Index>(i)));
        }

        /**
         * @brief Element-wise access
         * @param i index
         * @return Interval for element i in Box
         */
        Interval operator[](const size_t i) const
        {
            if (i >= static_cast<size_t>(x_lb.size()))
                throw std::out_of_range("Index out of range");
            return Interval(x_lb(static_cast<Eigen::Index>(i)), x_ub(static_cast<Eigen::Index>(i)));
        }

        /**
         * @brief get size of Box object
         * @return size of box
         */
        size_t size() const
        {
            return x_lb.size();
        }

        // project onto box

        /**
         * @brief Projects vector onto the Box
         * @param x vector reference
         */
        virtual void project(Eigen::Ref<Eigen::Vector<zono_float, -1>> x) const
        {
            if (x.size() != x_lb.size())
                throw std::invalid_argument("x must have the same size as the Box");
            x = x.cwiseMax(x_lb).cwiseMin(x_ub);
        }

        /**
         * @brief Clone operation
         * @return pointer to newly created object
         */
        virtual Box* clone() const
        {
            return new Box(*this);
        }

        // access bounds
        /**
         * @brief Get lower bounds
         * @return const reference to lower bounds
         */
        const Eigen::Vector<zono_float, -1>& lower() const { return x_lb; }

        /**
         * @brief Get upper bounds
         * @return const reference to upper bounds
         */
        const Eigen::Vector<zono_float, -1>& upper() const { return x_ub; }

        // width of box
        /**
         * @brief Get width of box
         * @return width of box
         *
         * Specifically, this returns the sum of the widths of each interval in the box
         */
        zono_float width() const
        {
            zono_float w = 0;
            for (Eigen::Index i=0; i<x_lb.size(); i++)
            {
                w += x_ub(i) - x_lb(i);
            }
            return w;
        }

        /**
         * @brief get center of box
         * @return center of box
         */
        Eigen::Vector<zono_float, -1> center() const
        {
            Eigen::Vector<zono_float, -1> c (this->size());
            for (Eigen::Index i=0; i<static_cast<Eigen::Index>(this->size()); i++)
            {
                c(i) = (*this)[i].center();
            }
            return c;
        }

        // operator overloading

        /**
         * @brief elementwise addition
         * @param other rhs box
         * @return this + other (elementwise)
         */
        Box operator+(const Box& other) const
        {
            if (this->size() != other.size())
                throw std::invalid_argument("Box addition: inconsistent dimensions");
            Box out =  *this;
            for (size_t i=0; i<this->size(); ++i)
            {
                out[i] = (*this)[i] + other[i];
            }
            return out;
        }

        /**
         * @brief elementwise subtraction
         * @param other rhs box
         * @return this - other (elementwise)
         */
        Box operator-(const Box& other) const
        {
            if (this->size() != other.size())
                throw std::invalid_argument("Box subtraction: inconsistent dimensions");
            Box out =  *this;
            for (size_t i=0; i<this->size(); ++i)
            {
                out[i] = (*this)[i] - other[i];
            }
            return out;
        }

        /**
         * @brief elementwise multiplication
         * @param other rhs box
         * @return this * other (elementwise)
         */
        Box operator*(const Box& other) const
        {
            if (this->size() != other.size())
                throw std::invalid_argument("Box multiplication: inconsistent dimensions");
            Box out =  *this;
            for (size_t i=0; i<this->size(); ++i)
            {
                out[i] = (*this)[i] * other[i];
            }
            return out;
        }

        /**
         * @brief elementwise multiplication with scalar
         * @param alpha scalar multiplier
         * @return alpha * this (elementwise)
         */
        Box operator*(zono_float alpha) const
        {
            Box out = *this;
            for (size_t i=0; i<this->size(); ++i)
            {
                out[i] = (*this)[i]*alpha;
            }
            return out;
        }

        /**
         * @brief elementwise division
         * @param other rhs box
         * @return this / other (elementwise)
         */
        Box operator/(const Box& other) const
        {
            if (this->size() != other.size())
                throw std::invalid_argument("Box division: inconsistent dimensions");
            Box out = *this;
            for (size_t i=0; i<this->size(); ++i)
            {
                out[i] = (*this)[i] / other[i];
            }
            return out;
        }

        // interval contractors

        /**
         * @brief Interval contractor
         * @param A constraint matrix (row-major)
         * @param b constraint vector
         * @param iter number of contractor iterations
         * @return flag indicating that the contractor did not detect that A*x=b and the box do not intersect
         *
         * Executes a forward-backward interval contractor for the equality constraint A*x=b.
         * For points x in the box, this shrinks the box without removing any points x that satisfy A*x=b.
         * If the contractor detects that the box does not intersect A*x=b, then this function will return false.
         */
        bool contract(const Eigen::SparseMatrix<zono_float, Eigen::RowMajor>& A, const Eigen::Vector<zono_float, -1>& b, const int iter)
        {
            if (iter <= 0)
                throw std::invalid_argument("iter must be positive");

            // contract over all constraints
            std::set<int> constraints;
            for (int i=0; i<A.rows(); i++)
            {
                constraints.insert(i);
            }

            // run contractor
            return contract_helper(A, b, iter, constraints);
        }

        /**
         * @brief Interval contractor over a subset of the dimensions of the box
         * @param A_rm constraint matrix, row major
         * @param b constraint vector
         * @param iter number of contractor iterations
         * @param A constraint matrix, column major
         * @param inds box dimension indices
         * @param tree_search_depth how deep to search constraint tree
         * @return flag indicating that the contractor did not detect that A*x=b and the box do not intersect
         *
         * This is a forward-backward contractor over a subset of the dimensions of the box.
         * This detects what other dimensions are affected up to a specified search depth prior to executing the contractor.
         */
        bool contract_subset(const Eigen::SparseMatrix<zono_float, Eigen::RowMajor>& A_rm, const Eigen::Vector<zono_float, -1>& b, int iter,
                             const Eigen::SparseMatrix<zono_float>& A, const std::set<int>& inds, int tree_search_depth)
        {
            if (iter <= 0)
                throw std::invalid_argument("iter must be positive");
            if (A_rm.rows() != A.rows() || A_rm.cols() != A.cols())
                throw std::invalid_argument("A_rm must equal A");

            // get affected constraints
            std::set<int> all_constraints, all_vars;

            get_vars_cons(A, A_rm, all_constraints, all_vars, inds, 0, tree_search_depth);

            // run contractor
            return contract_helper(A_rm, b, iter, all_constraints);
        }

        /**
         * @brief Linear map of box based on interval arithmetic
         * @param A map matrix (dense)
         * @return Linear mapped box
         */
        Box linear_map(const Eigen::Matrix<zono_float, -1, -1>& A) const
        {
            // input handling
            if (A.cols() != x_lb.size())
                throw std::invalid_argument("Matrix A must have the same number of columns as the size of the Box");

            // declare
            Box y(A.rows());

            // linear map
            for (int i=0; i<A.rows(); i++)
            {
                y[i] = Interval(0, 0);
                for (int j=0; j<A.cols(); j++)
                {
                    y[i].add_assign(y[i], ((*this)[j]*A(i, j)).as_view());
                }
            }
            return y;
        }

        /**
         * @brief Linear map of box based on interval arithmetic
         * @param A map matrix (sparse row major)
         * @return Linear mapped box
         */
        Box linear_map(const Eigen::SparseMatrix<zono_float, Eigen::RowMajor>& A) const
        {
            // input handling
            if (A.cols() != x_lb.size())
                throw std::invalid_argument("Matrix A must have the same number of columns as the size of the Box");

            // declare
            Box y (A.rows());

            // linear map
            for (int i=0; i<A.rows(); i++)
            {
                y[i] = Interval(0, 0);
                for (Eigen::SparseMatrix<zono_float, Eigen::RowMajor>::InnerIterator it(A, i); it; ++it)
                {
                    y[i].add_assign(y[i], ((*this)[it.col()]*it.value()).as_view());
                }
            }
            return y;
        }

        /**
         * @brief Linear map with vector
         * @param x vector
         * @return Interval
         */
        Interval dot(const Eigen::Vector<zono_float, -1>& x) const
        {
            // input handling
            if (x.size() != x_lb.size())
                throw std::invalid_argument("Vector x must have the same size as the Box");

            // declare
            Interval y(0, 0);

            // linear map
            for (int i=0; i<this->x_lb.size(); i++)
                y.add_assign(y, ((*this)[i]*x(i)));
            return y;
        }

        /**
         * @brief Permutes in place using permutation matrix, i.e., [x] <- P*[x]
         * @param P permutation matrix
         */
        void permute(const Eigen::PermutationMatrix<Eigen::Dynamic, Eigen::Dynamic>& P)
        {
            this->x_lb = P*this->x_lb;
            this->x_ub = P*this->x_ub;
        }

        /**
         * @brief Print method
         * @return string display of Box
         */
        std::string print() const
        {
            std::stringstream ss;
            ss << "Box: " << std::endl;
            for (Eigen::Index i=0; i<x_lb.size(); i++)
            {
                ss << "  " << (*this)[i] << std::endl;
            }
            return ss.str();
        }

        /**
         * @brief print to ostream
         * @param os ostream
         * @param box reference to box
         * @return ostream
         */
        friend std::ostream& operator<<(std::ostream& os, const Box& box)
        {
            os << box.print();
            return os;
        }

    protected:

        // members
        /// vector of lower bounds
        Eigen::Vector<zono_float, -1> x_lb;

        /// vector of upper bounds
        Eigen::Vector<zono_float, -1> x_ub;

    private:

        // back end for contraction operator

        /**
         * @brief Back-end for contractor
         * @param A constraint matrix (row-major)
         * @param b constraint vector
         * @param iter number of contractor iterations
         * @param constraints constraints to consider
         * @return flag indicating that the contractor did not detect that A*x=b and the box do not intersect
         */
        bool contract_helper(const Eigen::SparseMatrix<zono_float, Eigen::RowMajor>& A, const Eigen::Vector<zono_float, -1>& b, const int iter,
                             const std::set<int>& constraints)
        {
            for (int i=0; i<iter; i++)
            {
                // loop through constraints
                for (const int k : constraints)
                {
                    // forward propagate
                    Interval y(0, 0);
                    std::vector<int> cols; // keeping track of columns
                    for (Eigen::SparseMatrix<zono_float, Eigen::RowMajor>::InnerIterator it(A, k); it; ++it)
                    {
                        y.add_assign(y, (*this)[it.col()].to_interval()*it.value());
                        cols.push_back(static_cast<int>(it.col()));
                    }

                    // check validity
                    if (!y.contains(b(k)))
                        return false;
                    else
                        y = Interval(b(k), b(k));

                    // backward propagate
                    for (const int col : cols)
                    {
                        Interval x = y; // init
                        zono_float a_col=one;
                        for (Eigen::SparseMatrix<zono_float, Eigen::RowMajor>::InnerIterator it(A, k); it; ++it)
                        {
                            if (it.col() != col)
                            {
                                x.add_assign(x, (*this)[it.col()].to_interval()*(-it.value()));
                            }
                            else
                            {
                                a_col = it.value();
                            }
                        }

                        // update interval
                        (*this)[col].intersect_assign((*this)[col], (x * (one/a_col)).as_view());
                    }
                }
            }

            return true; // constraints valid
        }

        /**
         * @brief Search constraint tree for affected dimensions of box (recursive)
         * @param A constraint matrix (column major)
         * @param A_rm constraint matrix (row major)
         * @param constraints constraints to search
         * @param vars indices to consider
         * @param new_vars all affected indices (reference)
         * @param depth current depth in constraint tree
         * @param max_depth max depth to search constraint tree
         */
        void get_vars_cons(const Eigen::SparseMatrix<zono_float>& A, const Eigen::SparseMatrix<zono_float, Eigen::RowMajor>& A_rm,
                           std::set<int>& constraints, std::set<int>& vars, const std::set<int>& new_vars, int depth, int max_depth)
        {
            // immediately copy over constraints and vars
            vars.insert(new_vars.begin(), new_vars.end());

            // find new constraints
            std::set<int> new_constraints;
            for (const int i : new_vars)
            {
                for (Eigen::SparseMatrix<zono_float>::InnerIterator it(A, i); it; ++it)
                {
                    if (!constraints.count(static_cast<int>(it.row())))
                    {
                        new_constraints.insert(static_cast<int>(it.row()));
                    }
                }
            }

            // find new vars
            std::set<int> new_new_vars;
            for (const int i : new_constraints)
            {
                for (Eigen::SparseMatrix<zono_float, Eigen::RowMajor>::InnerIterator it(A_rm, i); it; ++it)
                {
                    if (!vars.count(static_cast<int>(it.col())))
                    {
                        new_new_vars.insert(static_cast<int>(it.col()));
                    }
                }
            }

            // add new constraints to set
            constraints.insert(new_constraints.begin(), new_constraints.end());

            // recurse if able
            depth++;
            if (depth < max_depth && new_new_vars.empty())
                get_vars_cons(A, A_rm, constraints, vars, new_new_vars, depth, max_depth);
        }
    };

} // namespace ZonoOpt


#endif